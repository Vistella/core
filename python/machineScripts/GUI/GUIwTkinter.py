from tkinter import *
import tkinter as tk
import tkinter.font as font
from PIL import ImageTk, Image



window = tk.Tk()

window.title("EL TEST")
window.geometry("800x800")
# add label
lbl = Label(window, text="output image", font=("Arial Bold", 15))
lbl.place(relx=0.5, rely=0.2, anchor=CENTER)# label position
# Add button
# define font
myFont = font.Font(family='Courier', size=20, weight='bold')
# Add button
btn = Button(window, text="Run Test", bg="orange", fg="red",
             width=10,height=2, compound="c")
# apply font to the button label
btn['font'] = myFont
# add button to gui window
# btn.pack()

#btn.grid(column=250, row=1) # botton position
btn.place(relx=0.5, rely=0.05, anchor=CENTER)

### open Image
path = "robot.jpg"
##
###Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
img = Image.open(path)
img = img.resize((500, 200), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
panel = tk.Label(window, image=img)
panel.image = img
# panel.grid(column=0, row=4, columnspan = 4)
panel.place(relx=0.5, rely=0.5, anchor=CENTER)
             
window.mainloop()

#


