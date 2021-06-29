#Create Window
# 5 Buttons for: Run test, Good/Bad Quality, Cancel/Retake, Save
# Filenames: DATE_TIME_LABEL.jpg ==> AWS
# DB Entry: string id, filname, label, timestamp

#1. Take image on EL1 --> 10-20s (os("-raspistill -ss 20000")) NOT picamera.Camera(....)
#2. Log into EL2
#3. Take image on EL2 --> 10-20s
#4. Transfer EL2 image to EL1
#5. Combine images
#6. Display on GUI --> tkinter (tk)