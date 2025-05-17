import qrcode
from PyPDF2 import PdfMerger
from IPython.display import Image
from PIL import Image, ImageFont, ImageDraw, ImageOps
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Generate solar panel labels with QR codes')
    parser.add_argument('start_id', type=int, help='Starting panel ID')
    parser.add_argument('end_id', type=int, help='Ending panel ID')
    args = parser.parse_args()

    # Create results directory if it doesn't exist
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    startID = args.start_id
    endID = args.end_id

    for x in range(startID, endID + 1):
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
        img = img.convert('RGB')  # Convert to RGB format

        font = ImageFont.truetype("/Library/Fonts/Microsoft/Arial.ttf", 30)

        background = Image.open("SolarPanelLabel.png")
        background = background.convert('RGB')  # Ensure background is in RGB mode
        
        # Calculate the position for the QR code
        qr_position = (720-22*length, 1141-22*length)
        background.paste(img, qr_position)
        
        txt = Image.new('L', (220, 50))
        d = ImageDraw.Draw(txt)
        d.text((0, 0), "panel_id " + s1, font=font, fill=255)
        w = txt.rotate(90, expand=1)
        
        # Calculate the position for the text
        text_position = (720-25*length, 1141-280)
        background.paste(ImageOps.colorize(w, (0, 0, 0), (0, 0, 0)), text_position, w)
        
        # Save individual PDFs in results directory
        output_path = os.path.join(results_dir, s1 + ".pdf")
        background.save(output_path)

    # Create list of PDFs in results directory
    pdfs = [os.path.join(results_dir, f'{panel_id:05d}.pdf') for panel_id in range(startID, endID+1)]

    merger = PdfMerger()

    for pdf in pdfs:
        merger.append(pdf)

    # Save final merged PDF in results directory
    merger.write(os.path.join(results_dir, "result.pdf"))
    merger.close()

if __name__ == "__main__":
    main()

