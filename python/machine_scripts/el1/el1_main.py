from datetime import datetime
import tkinter as tk
from tkinter import simpledialog
from PIL import ImageTk, Image  
import os
from tkinter import messagebox
from subprocess import Popen

#Create window with screen size
window = tk.Tk()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.title("Vistella - Electroluminisence Test")
window.geometry(str(screen_width)+'x'+str(screen_height))

def run_clicked():
    #Get Date
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #Start Photo taking on EL2 - Check that the file does exist in the right location on EL2
    p = Popen("ssh pi@192.168.8.11 'cd ~ && python3 /home/pi/core/python/machine_scripts/el2/el2_main.py'", shell=True) #Start long lasting command
    # ... do other stuff while subprocess is running
    #Take image on EL1
    os.system('raspistill -ss 200000 -sh 100 -ISO 2000 -co 50 -o /home/pi/el1_image.png')
    #Copy from EL2 to EL1
    os.system('scp pi@192.168.8.22:/home/pi/el2_image.png /home/pi/')

    p.terminate()

    images = [Image.open(x) for x in ['/home/pi/el1_image.png', '/home/pi/el2_image.png']] #Both images
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

    img = img.resize((int(.9*screen_width), int(0.9*screen_height)), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(window, image=img)
    panel.image = img
    panel.grid(column=0, row=4, columnspan=4)
    print("Run")

def save_clicked():
    print("Save")

def delete_clicked():
    os.remove('/home/pi/el_images/' + str(date) +'.jpg')
    print("Delete")


#Add buttons
run_button = tk.Button(window, text="Run EL test", command=run_clicked)
saved_button = tk.Button(window, text="Save Image", command=save_clicked)
delete_button = tk.Button(window, text="Delete Image", command=delete_clicked)
run_button.grid(column=1, row=1) 
saved_button.grid(column=2, row=1) 
delete_button.grid(column=3, row=1)


#btn.grid(column=2, row=1)            


window.mainloop()

