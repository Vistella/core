#!/usr/bin/env python3
from time import sleep
from picamera import PiCamera
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog
from PIL import ImageTk, Image  
import os
from tkinter import messagebox

camera = PiCamera()
camera.resolution = (1024, 786)#(2592, 1944) 


def run_clicked():
    date = datetime.now()
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    #camera warm-up time
    #camera.start_preview(alpha=200)
    camera.annotate_text = str(date) + ", Panel ID: " + user_input.get()
    camera.exposure_mode = 'night'
    sleep(3)
    camera.capture("/home/pi/" + user_input.get() + ".jpg")
    #camera.stop_preview()
    img = Image.open("/home/pi/" + user_input.get() + ".jpg")
    img = img.resize((500, 500), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(window, image=img)
    panel.image = img
    panel.grid(column=0, row=4, columnspan = 4)
    
    res = messagebox.askquestion('Quality Check', 'Save image to database?')
    if res == 'yes':
        pass
    elif res == 'no':
        os.remove("/home/pi/" + user_input.get() + ".jpg")
    else:
        messagebox.showwarning('error', 'Something went wrong!')

    
window = tk.Tk()

window.title("Run EL Test")
window.geometry('500x600')
lbl = tk.Label(window, text="Insert panel ID", font=("Arial Bold", 10))
lbl.grid(column=0, row=1)
user_input = tk.Entry(window,width=10)
user_input.grid(column=1, row=1)
btn = tk.Button(window, text="Run EL test", command=run_clicked)
btn.grid(column=2, row=1)            

window.mainloop()


