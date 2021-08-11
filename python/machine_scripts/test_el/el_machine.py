import subprocess
import os
from time import sleep
from picamera import PiCamera
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog
from PIL import ImageTk, Image
from tkinter import messagebox
import sys
from PIL import Image
import boto3
from botocore.exceptions import NoCredentialsError
import psycopg2
import csv

ACCESS_KEY = 'AKIAYUCNSKWSY4QVTQ7G'
SECRET_KEY = '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'

camera = PiCamera()
camera.resolution = (1024, 786)
# (2592, 1944)

from csv import writer
def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        #print("file is open")
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)
        #print('list is added')

def run_clicked():
    date = datetime.now()
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    camera.annotate_text = str(date)
    camera.exposure_mode = 'night'
    sleep(2)
    camera.capture("/home/pi/EL.jpg")

    subprocess.check_output("ssh pi@192.168.8.11 'cd ~ && python /home/pi/Documents/remote.py'", shell=True)
    os.system('scp pi@192.168.8.11:/home/pi/test.jpg /home/pi/')
    images = [Image.open(x) for x in ['/home/pi/test.jpg', '/home/pi/EL.jpg']]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    new_im.save('/home/pi/EL_images/' + str(date) +'.jpg')
    img = Image.open('/home/pi/EL_images/' + str(date) +'.jpg')
    img = img.resize((500, 250), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(window, image=img)
    panel.image = img
    panel.grid(column=0, row=4, columnspan=4)
    
    quality=messagebox.askquestion('Quality Check', 'Is the quality acceptable?')
    if quality == 'yes':
        Q=' good'
    else:
        Q=' bad'
    res = messagebox.askquestion('Send to DB', 'Save image to database?')
    if res == 'yes':
        path='/home/pi/EL_images/local_database/'+str(date[:10])+'/'
        append_list_as_row(db_file_name, [str(date),Q])
        print('go to wriete',str(date),Q)
        if os.path.isdir(path):
        
            new_im.save( path+ str(date) +'.jpg')
        else:
            os.mkdir(path)
            new_im.save( path+ str(date) +'.jpg')
        
            
#         uploaded = upload_to_aws('/home/pi/EL_images/' + str(date) +'.jpg', 'production-el-test-string', str(date) +'.jpg')
#         conn = psycopg2.connect(user="ukvuowsb", password="xOy8nq3xddLpXCYoioU2q1r9O_0iFkkt", host="tai.db.elephantsql.com",port="5432",database="ukvuowsb")
#         cur = conn.cursor()
#         cur.execute("INSERT INTO production.string_el_image (created_At, s3_filename) VALUES (%s, %s)",(str(date), str(date) +'.jpg'))
#         conn.commit()

    elif res == 'no':
        os.remove('/home/pi/EL_images/' + str(date) +'.jpg')
    else:
        messagebox.showwarning('error', 'Something went wrong!')
    


date = datetime.now()
date = date.strftime("%Y-%m-%d %H:%M:%S")
window = tk.Tk()

window.title("Run EL Test")
window.geometry('1200x800')
db_file_name='/home/pi/EL_images/Celles_quality_DB'+str(date[:10])+'.csv'
with open(db_file_name, 'w', newline='') as csvfile:
    makeDB = csv.writer(csvfile, delimiter=',')
                                    #uotechar='|', quoting=csv.QUOTE_MINIMAL)
    makeDB.writerow(['   Image Name      '] + [' Quality'])
btn = tk.Button(window, text="Run EL test", command=run_clicked)
btn.grid(column=2, row=1)


window.mainloop()



