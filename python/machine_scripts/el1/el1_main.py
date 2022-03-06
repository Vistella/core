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
    im = cv2.filter2D(resized_border, -1, kernel)
    # return the warped image
    return im



#Create window with screen size
window = tk.Tk()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.title("Vistella - Electroluminisence Test")
window.geometry(str(screen_width)+'x'+str(screen_height))
power = LED(21)

def run_clicked():
    #Get Date
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    power.on()
    #Start Photo taking on EL2 - Check that the file does exist in the right location on EL2
    p = Popen("ssh pi@192.168.8.22 'cd ~ && python3 /home/pi/core/python/machine_scripts/el2/el2_main.py'", shell=True) #Start long lasting command
    # ... do other stuff while subprocess is running
    #Take image on EL1
    os.system('raspistill -ss 3000000 -sh 100 -ISO 800 -co 50 -o /home/pi/el1_image.png')
    print('EL1 image taken')
    #Copy from EL2 to EL1
    os.system('scp pi@192.168.8.22:/home/pi/el2_image.png /home/pi/')

    p.terminate()
    left_cells = cv2.imread('/home/pi/el2_image.png')
    right_cells = cv2.imread('/home/pi/el1_image.png')
    
    # define the points for the 5 left cells that will be shown on top
    pts_top = []
    pts_top.append(np.array([(50, 760), (470, 710), (500, 1320), (75, 1290)], dtype = "float32"))
    pts_top.append(np.array([(470, 710), (1080, 660), (1100, 1340), (500, 1320)], dtype = "float32"))
    pts_top.append(np.array([(1080, 660), (1740, 650), (1760, 1310), (1100, 1340)], dtype = "float32"))
    pts_top.append(np.array([(1730, 650), (2235, 670), (2250, 1240), (1750, 1310)], dtype = "float32"))
    pts_top.append(np.array([(2235, 670), (2550, 700), (2550, 1190), (2250, 1240)], dtype = "float32"))
    # define the points for the 5 right cells that will be shown on bottom
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
        
    cv2.imwrite('/home/pi/el_images/' + str(date) +'.jpg', combined)
 
    img = Image.open('/home/pi/el_images/' + str(date) +'.jpg')
    width, height =(img.size) #Get combined dimensions
    img = img.resize((int(screen_width), int(height*(screen_width/width))), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(window, image=img)
    panel.image = img
    panel.grid(column=0, row=4, columnspan=30)
    text = tk.Label(window, text="Successfully Ran")
    text.grid(column=4, row=1)
    print("Run")
    power.off()

def good():
    save_clicked("good")

def bad():
    save_clicked("bad")

def save_clicked(quality):    
    text = tk.Label(window, text="String uploading...")
    text.place(x=570,y=5)
    conn = psycopg2.connect(user="jzztvyjdirgomm", password="974386311e9bf8265574baead65862ee677601c0f8e05bc954785e899d86dfaa", host="ec2-34-247-151-118.eu-west-1.compute.amazonaws.com",port="5432",database="djaki03gmcu3o")
    cur = conn.cursor()
    #Create panel
    cur.execute("INSERT INTO production.string (id, quality) VALUES ({},{})".format(dataEntry.get(), quality))
    conn.commit()
    text = tk.Label(window, text="String uploaded")
    print("Saved")

def delete_clicked():
    os.remove('/home/pi/el_images/' + str(date) +'.jpg')
    text = tk.Label(window, text="Image Deleted")
    text.place(x=570,y=5)
    print("Deleted" + 'el_images/' + str(date) +'.jpg')


#Add buttons
run_button = tk.Button(window, text="Run EL test", command=run_clicked)
good_button = tk.Button(window, text="Good", command=good)
bad_button = tk.Button(window, text="Bad", command=bad)
delete_button = tk.Button(window, text="Delete Image", command=delete_clicked)
dataEntry = tk.Entry(window)
labelText = tk.StringVar()
labelText.set("Enter String ID")
infoLabel = tk.Label(window, textvariable= labelText)
infoLabel.grid(column=0, row=1) 
dataEntry.grid(column=1, row=1)
run_button.grid(column=2, row=1) 
good_button.grid(column=3, row=1) 
bad_button.grid(column=4, row=1) 
delete_button.grid(column=5, row=1)
img = Image.open('/home/pi/logo.png')
width, height =(img.size) #Get combined dimensions
img = img.resize((int(screen_width), int(height*(screen_width/width))), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
panel = tk.Label(window, image=img)
panel.image = img
panel.grid(column=0, row=4, columnspan=30)       
window.bind("<Enter>", run_clicked)
window.mainloop()

