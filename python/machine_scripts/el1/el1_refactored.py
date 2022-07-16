from datetime import datetime
import tkinter as tk
from PIL import ImageTk, Image
#from gpiozero import LED
import os
import psycopg2
from subprocess import Popen
import numpy as np
import cv2
import pandas as pd



#Support functions
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
  
def gamma_trans(img, gamma):
    #adjust exposure
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

#Initilaize
#Read possible panels types
query = """
SELECT
pspt.id, 
pspt.name
FROM production.solar_panel_type pspt
"""
panel_types = read_query_as_df(query)
#power = LED(21)
date = 0

#UI setup
font_type = ("Courier", 20)

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

window.bind("<Enter>", run_clicked)
window.mainloop()
