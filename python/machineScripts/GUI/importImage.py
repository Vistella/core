from tkinter import *  
from PIL import ImageTk,Image  
root = Tk()  
canvas = Canvas(root, width = 300, height = 300)  
canvas.pack()  
img = ImageTk.PhotoImage(Image.open("robot.jpg"))  
canvas.create_image(20, 20, anchor="center", image=img)
#canvas.create_image(0, 0, anchor="center", image=img)
canvas.place(relx=0.5, rely=0.5, anchor="center")
root.mainloop()
