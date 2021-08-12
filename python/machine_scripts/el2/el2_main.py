from datetime import datetime
import tkinter as tk
from tkinter import simpledialog
from PIL import ImageTk, Image  
import os
#from tkinter import messagebox
from subprocess import Popen


os.system('raspistill -ss 200000 -sh 100 -ISO 2000 -co 50 -o /home/pi/el2_image.png')
