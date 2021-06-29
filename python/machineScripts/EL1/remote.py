from picamera import PiCamera
from time import sleep
camera = PiCamera()
camera.resolution = (1024, 786)#(2592, 1944) 

camera.exposure_mode = 'night'
sleep(2)
camera.capture("/home/pi/test.jpg")
