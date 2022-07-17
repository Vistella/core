#!/usr/bin/python3
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog
from PIL import ImageTk, Image
from gpiozero import LED
import os
import psycopg2
#from tkinter import messagebox
from subprocess import Popen

# import the necessary packages for image processing
import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib.pylab import cm
import pandas as pd

font_type = ("Courier", 20)
def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect

#adjust exposure
def gamma_trans(img, gamma):
    gamma_table=[np.power(x/255.0,gamma)*255.0 for x in range(256)]
    gamma_table=np.round(np.array(gamma_table)).astype(np.uint8)
    return cv2.LUT(img,gamma_table)

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = gamma_trans(image, 0.6)
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    resized = cv2.resize(warped, (400,400), interpolation = cv2.INTER_AREA)
    resized_border = cv2.copyMakeBorder(resized,2,2,2,2,cv2.BORDER_CONSTANT, value = [255,255,255])
    kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
    # return the warped image
    return cv2.filter2D(resized_border, -1, kernel)

def read_query_as_df(query):
    connection = None
    connection = psycopg2.connect(user="jzztvyjdirgomm", password="974386311e9bf8265574baead65862ee677601c0f8e05bc954785e899d86dfaa", host="ec2-34-247-151-118.eu-west-1.compute.amazonaws.com",port="5432",database="djaki03gmcu3o")
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
    connection.close
    return df

#Read possible panels types
query = """
SELECT
pspt.id, 
pspt.name
FROM production.solar_panel_type pspt
"""
panel_types = read_query_as_df(query)
print(panel_types)

#Create window with screen size
window = tk.Tk()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.title("Vistella - Electroluminisence Test")
window.geometry(f'{str(screen_width)}x{str(screen_height)}')

#Add drop_down
options = tk.StringVar(window)
options.set(panel_types["name"].iloc[0]) # default value
optionMenu1 =tk.OptionMenu(window, options, *panel_types["name"])
optionMenu1.grid(row=1,column=7, sticky='nsew')
optionMenu1.config(font=font_type)
menu = window.nametowidget(optionMenu1.menuname)
menu.config(font=font_type) # set the drop down menu font

power = LED(21)
date = 0
def run_clicked(self):
    #Check for material
    labelText.set("Checking materials")
    window.update()
    enoughMaterial = True
    
    #Get material requirements for that string    
    query = """
        SELECT
        ppmr.material_id, ppmr.amount/pspt.string_count as amount
        FROM production.panel_material_req ppmr
        JOIN production.material pm
        ON pm.id = ppmr.material_id
        JOIN production.material_type pmt
        ON pmt.id = pm.material_type_id
        JOIN production.solar_panel_type pspt
        ON pspt.id = ppmr.panel_type_id
        WHERE pmt.type in ('Tabbing Ribbon', 'Solar Cell')
        AND ppmr.panel_type_id = %s
        """%(str(panel_types.index[panel_types['name'] == options.get()].tolist()[0]+1))
    material_req = read_query_as_df(query)
    print(material_req)
    conn = psycopg2.connect(user="jzztvyjdirgomm", password="974386311e9bf8265574baead65862ee677601c0f8e05bc954785e899d86dfaa", host="ec2-34-247-151-118.eu-west-1.compute.amazonaws.com",port="5432",database="djaki03gmcu3o")
    cur = conn.cursor()

    global queries
    queries = []
    string_id = dataEntry.get()
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
            labelText.set('Material', line["material_id"],' never added to production')
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
                labelText.set("Lot has enough material " + str(line["material_id"]))
                window.update()
                print("Lot has enough material",line["material_id"] ,"left. Stock: ", round(row["sum"],4), ", needed: ", round(line["amount"],4), ", new stock: ", round(row["sum"] - line["amount"],4))
                query = """INSERT INTO production.inventory_changelog (quantity, change_type_id, lot_id, panel_id) 
                VALUES (%s, 10, %s, %s, %s)
                """
                queries.append([query, [str(round(-line["amount"],4)), str(row["lot_id"]), str(string_id)]])
                line["amount"] = 0
            else:
                labelText.set("Multiple lots needed for material: " + str(round(line["material_id"],4)))
                window.update()
                print("Multiple lots needed for material:",round(line["material_id"],4) ,". Stock: ", round(row["sum"],4), ", needed: ", round(line["amount"],4), ", new stock: 0")
                #Reduce first lot to 0
                query = """INSERT INTO production.inventory_changelog (quantity, change_type_id, lot_id, panel_id)
                VALUES (%s, 10, %s, %s, %s)
                """
                queries.append([query, [str(round(-row["sum"],4)), str(row["lot_id"]), str(string_id)]])
                
                line["amount"] = round(line["amount"]- row["sum"],4) #Reduce lot by remaining stock
                
            if line["amount"] == 0:
                break
        if line["amount"] > 0:
            labelText.set('Not enough Material ' + str(line["material_id"]))
            window.update()
            enoughMaterial = False
            print("not enoughMaterial")
            break

    #Get Date
    global date
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    power.on()
    #Start Photo taking on EL2 - Check that the file does exist in the right location on EL2
    p = Popen("ssh pi@192.168.8.22 'cd ~ && python3 /home/pi/core/python/machine_scripts/el2/el2_main.py'", shell=True) #Start long lasting command
    # ... do other stuff while subprocess is running
    #Take image on EL1
    labelText.set('Take images')
    window.update()
    os.system('raspistill -ss 3000000 -sh 100 -ISO 800 -co 50 -o /home/pi/el1_image.png')
    print('EL1 image taken')
    #Copy from EL2 to EL1
    os.system('scp pi@192.168.8.22:/home/pi/el2_image.png /home/pi/')

    p.terminate()
    left_cells = cv2.imread('/home/pi/el2_image.png')
    right_cells = cv2.imread('/home/pi/el1_image.png')
    
    # define the points for the 5 left cells that will be shown on top
    pts_top = []
    pts_top.append(np.array([(40, 760), (470, 710), (500, 1320), (75, 1290)], dtype = "float32"))
    pts_top.append(np.array([(470, 710), (1080, 660), (1100, 1340), (500, 1320)], dtype = "float32"))
    pts_top.append(np.array([(1070, 650), (1720, 640), (1740, 1310), (1090, 1340)], dtype = "float32"))
    pts_top.append(np.array([(1710, 640), (2210, 660), (2225, 1230), (1730, 1300)], dtype = "float32"))
    pts_top.append(np.array([(2210, 670), (2530, 700), (2530, 1190), (2215, 1240)], dtype = "float32"))
    # define the points for the right cells that will be shown on bottom
    pts_bot = []
    pts_bot.append(np.array([(40, 700), (440, 680), (420, 1240), (25, 1190)], dtype = "float32"))
    pts_bot.append(np.array([(430, 680), (980, 685), (960, 1290), (410, 1240)], dtype = "float32"))
    pts_bot.append(np.array([(980, 685), (1570, 710), (1560, 1300), (960, 1290)], dtype = "float32"))
    pts_bot.append(np.array([(1570, 710), (2060, 750), (2040, 1280), (1560, 1300)], dtype = "float32"))
    pts_bot.append(np.array([(2060, 750), (2390, 780), (2370, 1250), (2040, 1280)], dtype = "float32"))


    # apply the four point tranform to obtain a "birds eye view" of
    # the images
    images_top = []
    for x in pts_top:
        images_top.append(four_point_transform(left_cells, x))

    images_bot = []
    for x in pts_bot:
        images_bot.append(four_point_transform(right_cells, x))

    #concat the images to a 2x5 matrix
    im_h_top = cv2.hconcat(images_top)
    im_h_bot = cv2.hconcat(images_bot)
    combined = cv2.vconcat([im_h_top,im_h_bot])

    #add a black border for text top and bottom
    combined = cv2.copyMakeBorder(combined, 50, 50, 0, 0, cv2.BORDER_CONSTANT)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for number in range(1,6):
        cv2.putText(combined, str(number), (-200+402*number,40), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    for number in range(6,11):
        cv2.putText(combined, str(number), (-200+402*(number-5),900), font,1, (255, 255, 255), 2, cv2.LINE_AA)
        
    
    colorized = cm.CMRmap(combined)
    cv2.imwrite('/home/pi/el_images/' + str(date) +'.jpg', colorized*255)
    img = Image.open('/home/pi/el_images/' + str(date) +'.jpg')
    width, height =(img.size) #Get combined dimensions
    img = img.resize((int(screen_width), int(height*(screen_width/width))), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(window, image=img)
    panel.image = img
    panel.grid(column=0, row=4, columnspan=30)
    text = tk.Label(window, text="Successfully Ran", font=font_type)
    text.grid(column=6, row=1)
    print("Run")
    power.off()
    good_button["state"] = "normal"
    bad_button["state"] = "normal"
    delete_button["state"] = "normal"
    conn.commit()
    conn.close()
    
def good():
    save_clicked("good")

def bad():
    save_clicked("bad")

def save_clicked(quality):    
    global date
    global queries
    string_id = dataEntry.get()

    #Write to db:
    conn = psycopg2.connect(user="jzztvyjdirgomm", password="974386311e9bf8265574baead65862ee677601c0f8e05bc954785e899d86dfaa", host="ec2-34-247-151-118.eu-west-1.compute.amazonaws.com",port="5432",database="djaki03gmcu3o")
    cur = conn.cursor()
    print(queries)
    for query, data in queries:
        cur.execute(query, data)
    conn.commit()
    conn.close()

    #rename image
    file_name = r'/home/pi/el_images/' + str(string_id) + "_" + quality + '.jpg'
    file_name.replace(" ", "_")
    print(file_name)
    print('scp ' + file_name +  ' vistella@167.235.50.52:/var/www/html/img/el_images')
    os.rename(r'/home/pi/el_images/' + str(date) +'.jpg', file_name)
    text = tk.Label(window, text="String uploading...",font=font_type)
    text.grid(column=6, row=1)
    conn = psycopg2.connect(user="jzztvyjdirgomm", password="974386311e9bf8265574baead65862ee677601c0f8e05bc954785e899d86dfaa", host="ec2-34-247-151-118.eu-west-1.compute.amazonaws.com",port="5432",database="djaki03gmcu3o")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO production.string (id)
        values(%s) 
        ON CONFLICT (id) 
        DO 
        UPDATE SET updated_at  = EXCLUDED.updated_at
    """%(string_id[1:]))
    cur.execute("INSERT INTO production.string_el (string_id, string_image_link, quality) VALUES ({},{},{})".format(string_id[1:],"'" + str(string_id) + "_" + quality + "'", "'" + quality + "'"))
    conn.commit()
    os.system('scp ' + file_name +  ' vistella@167.235.50.52:/var/www/html/img/el_images')
    os.remove('/home/pi/el2_image.png')
    
    text = tk.Label(window, text="String uploaded",  font=font_type)
    text.grid(column=6, row=1)
    print("Saved")
    conn.close()
    good_button["state"] = "disabled"
    bad_button["state"] = "disabled"
    delete_button["state"] = "disabled"

def delete_clicked():
    global date
    os.remove('/home/pi/el_images/' + str(date) +'.jpg')
    text = tk.Label(window, text="Image Deleted",  font=font_type)
    text.place(x=570,y=5)
    print("Deleted" + 'el_images/' + str(date) +'.jpg')
    good_button["state"] = "disabled"
    bad_button["state"] = "disabled"
    delete_button["state"] = "disabled"


#Add buttons
run_button = tk.Button(window, text="Run EL test", command=run_clicked,  font=font_type)
good_button = tk.Button(window, text="Good", command=good,  font=font_type)
bad_button = tk.Button(window, text="Bad", command=bad,  font=font_type)
delete_button = tk.Button(window, text="Delete Image", command=delete_clicked,  font=font_type)
dataEntry = tk.Entry(window,  font=font_type)
labelText = tk.StringVar()
labelText.set("Enter String ID")
infoLabel = tk.Label(window, textvariable= labelText,  font=font_type)
infoLabel.grid(column=0, row=1) 
dataEntry.grid(column=1, row=1)
run_button.grid(column=2, row=1) 
good_button.grid(column=3, row=1) 
bad_button.grid(column=4, row=1) 
delete_button.grid(column=5, row=1)
good_button["state"] = "disabled"
bad_button["state"] = "disabled"
delete_button["state"] = "disabled"
img = Image.open('/home/pi/logo.png')
width, height =(img.size) #Get combined dimensions
img = img.resize((int(screen_width), int(height*(screen_width/width))), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
panel = tk.Label(window, image=img)
panel.image = img
panel.grid(column=0, row=4, columnspan=30)       
#window.bind("<Enter>", run_clicked)
window.mainloop()

