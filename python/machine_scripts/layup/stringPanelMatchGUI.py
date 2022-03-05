import psycopg2
import psycopg2.extras
import tkinter as tk
import time

window = tk.Tk()
window.title("String to Panel matching")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(str(screen_width)+'x'+str(screen_height))

#frame = tk.Frame(window)
#frame.pack()

canvas = tk.Canvas(window, width=screen_width, height=0.8*screen_height, bg="white")
canvas.grid(row=3,column=0,columnspan = 5)
canvas.grid()
#canvas.pack()
id_string = []
id_label = []
id_string.append(tk.StringVar())
id_label.append(tk.Label(window, textvariable= id_string[-1], font=("Courier", 44), fg = "red"))
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
    if scanInputString:                    # Check that the input string is not empty
        if scanInputString[0].isdigit():   # Panel QR Codes start with integers, i.e. 00012
            panelId = scanInputString
            stringIds = [] #list to store the 6 strings

            canvas.itemconfig(oval_panel, fill="green")
            id_string[0].set(panelId)
            for x, item in enumerate(oval_string):
                canvas.itemconfig(item, fill="white")
                id_string[x+1].set("           ")
            labelText.set("Enter ID for String No. " + str(len(stringIds)+1))
        
        elif (scanInputString[1:], panelId) in stringIds:
            labelText.set("String already scanned")

        elif scanInputString[0] == 's' and (scanInputString[1:], panelId) not in stringIds and int(panelId) != 0:    # String QR Codes start with s, i.e. s00012
            stringIds.append((scanInputString[1:], panelId)) #save strings in db without leading 's'
            canvas.itemconfig(oval_string[len(stringIds)-1], fill="green")
            id_string[len(stringIds)].set(scanInputString)
            labelText.set("Enter ID for String No. " + str(len(stringIds)+1))
        if len(stringIds) == 6:            # If all strings are scanned, upload to DB
            labelText.set("Uploading....")
            #try:
            conn = psycopg2.connect(user="jzztvyjdirgomm", password="974386311e9bf8265574baead65862ee677601c0f8e05bc954785e899d86dfaa", host="ec2-34-247-151-118.eu-west-1.compute.amazonaws.com",port="5432",database="djaki03gmcu3o")
            cur = conn.cursor()
            #Create panel
            cur.execute("INSERT INTO production.solar_panel (id, panel_type_id) VALUES (%s, 1)"%(panelId))
            conn.commit()
            query = """INSERT INTO production.string (id, panel_id) VALUES (%s, %s)"""
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
            #labelText.set("Enter Panel ID")

    dataEntry.delete(0,"end")
    dataEntry.focus()
    print("PanelId: " + str(panelId))
    print("Strings: " + str(stringIds))
    return stringIds, panelId
window.bind("<Return>", scanQR)
dataEntry.focus()
window.mainloop()

