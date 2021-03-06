from tkinter import *
from PIL import ImageTk, Image
import os

class Application(Frame):
    def __init__(self, parent):
        Frame.__init__(self,parent)
        self.pack(fill=BOTH, expand=True)

        self.create_Menu()
        self.create_widgets()

    def create_Menu(self):
        self.menuBar = Menu(self)

        self.fileMenu = Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Open", command=self.getImage)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.exitProgram)

        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        root.config(menu=self.menuBar)

    def create_widgets(self):
        self.viewWindow = Canvas(self, bg="white")
        self.viewWindow.pack(side=TOP, fill=BOTH, expand=True)

    def getImage(self):
        imageFile = Image.open("robot.jpg")
        imageFile = ImageTk.PhotoImage(imageFile)

        self.viewWindow.image = imageFile
        self.viewWindow.create_image(width/2, height/2, anchor=CENTER, image=imageFile, tags="bg_img")

    def exitProgram(self):
        os._exit(0)

root = Tk()
root.title("Photo Zone")
root.wm_state('zoomed')

app = Application(root)

root.mainloop()

