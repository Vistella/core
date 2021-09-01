from datetime import datetime
import tkinter as tk
from tkinter import simpledialog
from PIL import ImageTk, Image  
import os
#from tkinter import messagebox
from subprocess import Popen
#Get Date
date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#Create window with screen size
window = tk.Tk()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.title("Vistella - Electroluminisence Test")
window.geometry(str(screen_width)+'x'+str(screen_height))

def run_clicked():
    #Get Date
    #date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #Start Photo taking on EL2 - Check that the file does exist in the right location on EL2
    p = Popen("ssh pi@192.168.8.22 'cd ~ && python3 /home/pi/core/python/machine_scripts/el2/el2_main.py'", shell=True) #Start long lasting command
    # ... do other stuff while subprocess is running
    #Take image on EL1
    os.system('raspistill -ss 3000000 -sh 100 -ISO 800 -co 50 -o /home/pi/el1_image.png')
    print('EL1 image taken')
    #Copy from EL2 to EL1
    os.system('scp pi@192.168.8.22:/home/pi/el2_image.png /home/pi/')

    p.terminate()

    images = [Image.open(x) for x in [ '/home/pi/el2_image.png','/home/pi/el1_image.png' ]] #Both images
    widths, heights = zip(*(i.size for i in images)) #Get combined dimensions
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    new_im.save('/home/pi/el_images/' + str(date) +'.jpg')
    img = Image.open('/home/pi/el_images/' + str(date) +'.jpg')

    img = img.resize((int(screen_width), int(1.85*screen_height*(max_height/total_width))), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(window, image=img)
    panel.image = img
    panel.grid(column=0, row=4, columnspan=30)
    text = tk.Label(window, text="Successfully Ran")
    text.grid(column=4, row=1)
    print("Run")

def save_clicked():    
    text = tk.Label(window, text="Image Saved")
    text.place(x=570,y=5)
    print("Saved")

def delete_clicked():
    os.remove('/home/pi/el_images/' + str(date) +'.jpg')
    text = tk.Label(window, text="Image Deleted")
    text.place(x=570,y=5)
    print("Deleted" + 'el_images/' + str(date) +'.jpg')


#Add buttons
run_button = tk.Button(window, text="Run EL test", command=run_clicked)
saved_button = tk.Button(window, text="Save Image", command=save_clicked)
delete_button = tk.Button(window, text="Delete Image", command=delete_clicked)
run_button.grid(column=1, row=1) 
saved_button.grid(column=2, row=1) 
delete_button.grid(column=3, row=1)
img = Image.open('/home/pi/logo.png')

img = img.resize((int(screen_width), int(screen_height)), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
panel = tk.Label(window, image=img)
panel.image = img
panel.grid(column=0, row=4, columnspan=30)
    


#btn.grid(column=2, row=1)            


window.mainloop()

