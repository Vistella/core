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

ACCESS_KEY = 'AKIAYUCNSKWSY4QVTQ7G'
SECRET_KEY = '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'

camera = PiCamera()
camera.resolution = (1024, 786)
# (2592, 1944)


def run_clicked():
    date = datetime.now()
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    camera.annotate_text = str(date)
    camera.exposure_mode = 'night'
    sleep(2)
    camera.capture("/home/pi/EL.jpg")

    subprocess.check_output("ssh pi@192.168.8.11 'cd ~ && python /home/pi/Documents/remote.py'", shell=True)
    os.system('scp pi@192.168.8.102:/home/pi/test.jpg /home/pi/')
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
    res = messagebox.askquestion('Quality Check', 'Save image to database?')
    if res == 'yes':
        uploaded = upload_to_aws('/home/pi/EL_images/' + str(date) +'.jpg', 'production-el-test-string', str(date) +'.jpg')
        conn = psycopg2.connect(user="ukvuowsb", password="xOy8nq3xddLpXCYoioU2q1r9O_0iFkkt", host="tai.db.elephantsql.com",port="5432",database="ukvuowsb")
        cur = conn.cursor()
        cur.execute("INSERT INTO production.string_el_image (created_At, s3_filename) VALUES (%s, %s)",(str(date), str(date) +'.jpg'))
        conn.commit()

    elif res == 'no':
        os.remove('/home/pi/EL_images/' + str(date) +'.jpg')
    else:
        messagebox.showwarning('error', 'Something went wrong!')

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

window = tk.Tk()

window.title("Run EL Test")
window.geometry('1200x800')
btn = tk.Button(window, text="Run EL test", command=run_clicked)
btn.grid(column=2, row=1)

window.mainloop()

