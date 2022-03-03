import psycopg2
import psycopg2.extras
import tkinter as tk
import time

window = tk.Tk()
window.title("String to Panel matching")
frame = tk.Frame(window)
frame.pack()

canvas = tk.Canvas(window, width=450, height=300, bg="white")
canvas.pack()

oval_panel = canvas.create_oval(10, 10, 30, 30, fill="white")
canvas.create_window(60, 20, window=tk.Label(window, text= "Panel"))
oval_string = []
for string in range(1,7):
    oval_string.append(canvas.create_oval(10, 10+30*string, 30, 30+30*string, fill="white"))
    canvas.create_window(60, 20+30*string, window=tk.Label(window, text= "String " + str(string)))
dataEntry = tk.Entry(window)
canvas.create_window(200, 140, window=dataEntry)
labelText = tk.StringVar()
labelText.set("Enter Panel ID")
infoLabel = tk.Label(window, textvariable= labelText)
canvas.create_window(200, 110, window=infoLabel)

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
            for item in oval_string:
                canvas.itemconfig(item, fill="white")
            labelText.set("Enter ID for String No. " + str(len(stringIds)+1))
        
        elif (scanInputString[1:], panelId) in stringIds:
            labelText.set("String already scanned")

        elif scanInputString[0] == 's' and (scanInputString[1:], panelId) not in stringIds and int(panelId) != 0:    # String QR Codes start with s, i.e. s00012
            stringIds.append((scanInputString[1:], panelId)) #save strings in db without leading 's'
            canvas.itemconfig(oval_string[len(stringIds)-1], fill="green")
            labelText.set("Enter ID for String No. " + str(len(stringIds)+1))
        if len(stringIds) == 6:            # If all strings are scanned, upload to DB
            #Write to DB
            #try:
            conn = psycopg2.connect(user="mjjyypvqfcescn", password="e93dc8ef167aa960b56248e5a2231cbc7d7ad5854266e7df2ab867763f065629", host="ec2-63-34-97-163.eu-west-1.compute.amazonaws.com",port="5432",database="d94t9tih4i30sp")
            cur = conn.cursor()
            #Create panel
            query = """INSERT INTO production.solar_panel (id, panel_type_id) VALUES (%s, 1)"""
            psycopg2.extras.execute_batch(cur, query, int(panelId))
            conn.commit()
            query = """INSERT INTO production.string_panel (string_id, panel_id) VALUES (%s, %s)"""
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
            #labelText.set("Enter Panel ID")

    dataEntry.delete(0,"end")
    dataEntry.focus()
    print("PanelId: " + str(panelId))
    print("Strings: " + str(stringIds))
    return stringIds, panelId
window.bind("<Return>", scanQR)
dataEntry.focus()
window.mainloop()

