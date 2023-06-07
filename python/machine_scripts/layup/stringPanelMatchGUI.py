import psycopg2
import psycopg2.extras
import tkinter as tk
import time
import pandas as pd
import json
import os

def read_query_as_df(query):
    connection = None
    connection = get_connection()
    cursor = connection.cursor()  
    temp = []
    result = None
    cursor.execute(query)
    results = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    connection.close()
    for result in results:
        result = list(result)
        temp.append(result)
    df = pd.DataFrame(temp, columns=colnames)
    connection.close()
    return df


def get_connection():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.abspath(os.path.join(script_directory, '../../../'))
    file_path = os.path.join(target_directory, "db_credentials.json")
    db = json.load(open(file_path))
    return psycopg2.connect(user = db["user"],
                     password = db["password"],
                     host = db["host"],
                     port = db["port"],
                     database = db["database"]
                     )
    
#Read possible panels types
query = """
SELECT
pspt.id, 
pspt.name
FROM production.solar_panel_type pspt
"""
panel_types = read_query_as_df(query)

window = tk.Tk()
window.title("String to Panel matching")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(str(screen_width)+'x'+str(screen_height))

canvas = tk.Canvas(window, width=screen_width, height=0.8*screen_height, bg="white")
canvas.grid(row=3,column=0,columnspan = 5)
canvas.grid()

#Add drop_down
options = tk.StringVar(window)
options.set(panel_types["name"].iloc[0]) # default value
optionMenu1 =tk.OptionMenu(window, options, *panel_types["name"])
optionMenu1.grid(row=1,column=3, sticky='nsew')
optionMenu1.config(font=("Courier", 44))
menu = window.nametowidget(optionMenu1.menuname)
menu.config(font=("Courier", 44)) # set the drop down menu font
id_string = [tk.StringVar()]
id_label = [tk.Label(window, textvariable=id_string[-1], font=("Courier", 44), fg="red")]

canvas.create_window(700, 100, window=id_label[-1])
oval_panel = canvas.create_oval(60, 60, 140, 140, fill="white")
canvas.create_window(300, 100, window=tk.Label(window, text= "Panel:", font=("Courier", 44)))
oval_string = []
for string in range(1,7):
    oval_string.append(canvas.create_oval(60, 60+100*string, 140, 140+100*string, fill="white"))
    canvas.create_window(350, 100+100*string, window=tk.Label(window, text= "String " + str(string) + ":", font=("Courier", 44)))
    # Displays the ID

    id_string.append(tk.StringVar())
    id_label.append(tk.Label(window, textvariable= id_string[-1], font=("Courier", 44), fg = "red"))
    canvas.create_window(700, 100+100*string, window=id_label[-1])
dataEntry = tk.Entry(window,  font=("Courier", 44))
dataEntry.grid(column=2, row=1)
#canvas.create_window(200, 140, window=dataEntry)
labelText = tk.StringVar()
labelText.set("Enter Panel ID")
infoLabel = tk.Label(window, textvariable= labelText, font=("Courier", 44))
infoLabel.grid(column=2, row=0)
#canvas.create_window(200, 110, window=infoLabel)
stringIds = [] #list to store the 6 strings
panelId = 0
def scanQR(event):
    global panelId
    global stringIds
    scanInputString = dataEntry.get()
    if scanInputString[0].isdigit():   # Panel QR Codes start with integers, i.e. 00012
        panelId = scanInputString
        stringIds = [] #list to store the 6 strings

        canvas.itemconfig(oval_panel, fill="green")
        id_string[0].set(panelId)
        for x, item in enumerate(oval_string):
            canvas.itemconfig(item, fill="white")
            id_string[x+1].set("           ")
        labelText.set("Enter ID for String No. " + str(len(stringIds)+1))

    elif (panelId, scanInputString[1:]) in stringIds:
        labelText.set("String already scanned")

    elif scanInputString[0] == 's' and (scanInputString[1:], panelId) not in stringIds and int(panelId) != 0:    # String QR Codes start with s, i.e. s00012
        #Check if the string exists in EL tests
        conn = get_connection()
        cur = conn.cursor()
        query = """SELECT count(ps.id)
        FROM production.string ps
        WHERE ps.id = %s """%(scanInputString[1:])
        cur.execute(query)
        result = cur.fetchall()
        if result[0][0] == 1:
            #string does exist
            stringIds.append((panelId, scanInputString[1:])) #save strings in db without leading 's'
            canvas.itemconfig(oval_string[len(stringIds)-1], fill="green")
            id_string[len(stringIds)].set(scanInputString)
            labelText.set("Enter ID for String No. " + str(len(stringIds)+1))
        elif result[0][0] == 0:
            #Error, string is missing in EL tests
            labelText.set("No String " + scanInputString[1:] +". EL first. Then scan string " + str(len(stringIds)+1))

    if len(stringIds) == 6:            # If all strings are scanned, upload to DB
        enoughMaterial = True
        labelText.set("Checking materials....")
        #Get material requirements for that string

        query = """
            SELECT
            ppmr.material_id, ppmr.amount as amount
            FROM production.panel_material_req ppmr
            JOIN production.material pm
            ON pm.id = ppmr.material_id
            JOIN production.material_type pmt
            ON pmt.id = pm.material_type_id
            JOIN production.solar_panel_type pspt
            ON pspt.id = ppmr.panel_type_id
            WHERE pmt.type in ('Solar Glass', 'Buss Ribbon', 'Tedlar', 'EVA')
            AND ppmr.panel_type_id = %s
            """%(str(panel_types.index[panel_types['name'] == options.get()].tolist()[0]+1))
        material_req = read_query_as_df(query)
        print(material_req)
        conn = get_connection()
        cur = conn.cursor()
        queries = []
        for index, line in material_req.iterrows():

            query = """
                SELECT 
                pic.lot_id, 
                sum(pic.quantity),
                min(pl.updated_at) as moved_to_prod
                FROM production.inventory_changelog pic
                JOIN production.lot pl
                ON pic.lot_id = pl.id
                JOIN finance.purchase_order_line ppol
                ON ppol.id = pl.purchase_order_line_id
                WHERE
                    bin_id = 2 AND
                    ppol.material_id = %s
                GROUP BY
                    pic.lot_id
            """%line["material_id"]
            available_lot = read_query_as_df(query)

            if available_lot.empty:
                labelText.set('Material ' +str(line["material_id"]) +' never added to production')
                window.update()
                print('Material', line["material_id"],'never added to production')
                enoughMaterial = False
                print("not enoughMaterial")
                break
            if available_lot["sum"].sum() == 0:
                labelText.set("No more material left")
                enoughMaterial = False
                print("not enoughMaterial")
                break
            #display(available_lot)
            for index2, row in available_lot.iterrows():
                if round(row["sum"],4) == 0: #if lot empty, go to the next lot
                    pass
                elif row["sum"] >= line["amount"]:
                    labelText.set("Lot has enough material " +str(line["material_id"]))
                    window.update()
                    print("Lot has enough material",line["material_id"] ,"left. Stock: ", round(row["sum"],4), ", needed: ", round(line["amount"],4), ", new stock: ", round(row["sum"] - line["amount"],4))
                    query = "INSERT INTO production.inventory_changelog (quantity, change_type_id, lot_id, panel_id) VALUES (%s, 10, %s, %s)"
                    queries.append([query, [str(round(-line["amount"],4)), str(row["lot_id"]), str(panelId)]])
                    line["amount"] = 0
                else:
                    labelText.set("Multiple lots needed for material: " + str(round(line["material_id"],4)))
                    window.update()
                    print("Multiple lots needed for material:",round(line["material_id"],4) ,". Stock: ", round(row["sum"],4), ", needed: ", round(line["amount"],4), ", new stock: 0")
                    #Reduce first lot to 0
                    query = "INSERT INTO production.inventory_changelog (quantity, change_type_id, lot_id, panel_id) VALUES (%s, 10, %s, %s)"
                    queries.append([query, [str(round(-line["amount"],4)), str(row["lot_id"]), str(panelId)]])

                    line["amount"] = round(line["amount"]- row["sum"],4) #Reduce lot by remaining stock

                if line["amount"] == 0:
                    break
            if line["amount"] > 0:
                labelText.set('Not enough Material' + str(line["material_id"]))
                window.update()
                enoughMaterial = False
                print("not enoughMaterial")
                break

        

        if  enoughMaterial:
            labelText.set("Uploading....")

            for query, data in queries:
                cur.execute(query, data)

            #Create panel
            cur.execute("INSERT INTO production.solar_panel (id, panel_type_id) VALUES (%s, 1)"%(panelId))
            conn.commit()
            query = """UPDATE production.string 
                SET panel_id = %s
                WHERE id = %s
            """
            psycopg2.extras.execute_batch(cur, query, stringIds)
            conn.commit()
            conn.close()
            labelText.set("data uploaded to db, enter new Panel ID")
            #except:
            #    labelText.set("Error during upload, String already in DB?")
            stringIds = []
            panelId = 0

            for k in range(1,3):
                canvas.itemconfig(oval_panel, fill="green")
                for item in oval_string:
                    canvas.itemconfig(item, fill="green")
                time.sleep(1)
                canvas.itemconfig(oval_panel, fill="white")
                for item in oval_string:
                    canvas.itemconfig(item, fill="white")
                time.sleep(1)
                for item in id_string:
                    item.set("           ")

    dataEntry.delete(0,"end")
    dataEntry.focus()
    print("PanelId: " + str(panelId))
    print("Strings: " + str(stringIds))
    return stringIds, panelId
window.bind("<Return>", scanQR)
dataEntry.focus()
window.mainloop()

