import qrcode
from PyPDF2 import PdfMerger  # Updated import here
from IPython.display import Image
from PIL import Image, ImageFont, ImageDraw, ImageOps
import tkinter as tk
from tkinter import simpledialog

ROOT = tk.Tk()

ROOT.withdraw()
# the input dialog
startID = simpledialog.askstring(title="Start Panel_ID", prompt="Start Panel_ID")
endID = simpledialog.askstring(title="End Panel_ID", prompt="End Panel_ID")                            

for x in range(int(startID), int(endID) + 1):
    panel_id = x
    s1 = f'{panel_id:05d}'
    length = 14
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=length,
        border=0,
    )
    qr.add_data(s1)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    font = ImageFont.truetype("/Library/Fonts/Microsoft/Arial.ttf", 30)

    background = Image.open("SolarPanelLabel.png")
    txt = Image.new('L', (220, 50))
    d = ImageDraw.Draw(txt)
    d.text((0, 0), "panel_id " + s1, font=font, fill=255)
    w = txt.rotate(90, expand=1)

    background.paste(img, (720-22*length, 1141-22*length))
    draw = ImageDraw.Draw(background)
    background.paste(ImageOps.colorize(w, (0, 0, 0), (0, 0, 0)), (720-25*length, 1141-280), w)
    background.save(s1 + ".pdf")

pdfs = [f'{panel_id:05d}.pdf' for panel_id in range(int(startID), int(endID)+1)]

merger = PdfMerger()  # Updated usage here

for pdf in pdfs:
    merger.append(pdf)

merger.write("result.pdf")
merger.close()
