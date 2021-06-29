from defisheye import Defisheye
import os
from PIL import Image
import cv2 
import numpy as np 

def make_square(im, min_size=256, fill_color=(0, 0, 0, 0)):
    x, y = im.size
    size = max(min_size, x, y)
    new_im = Image.new('RGBA', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    return new_im

os.system('raspistill -ss 200000 -sh 100 -ISO 2000 -co 50 -o /home/pi/testFisheye.png')
dtype = 'linear'
format = 'fullframe'
fov = 115
pfov = 100

def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result
  
test_image = cv2.imread("/home/pi/testFisheye.png")

result = rotate_image(test_image, 1)

# Locate points of the documents or object which you want to transform
pts1 = np.float32([[0, 0], [2592, 250], [0, 1944], [2592, 1700]])
pts2 = np.float32([[0, 0], [2592, 0], [0, 1944], [2592, 1944]])
  
# Apply Perspective Transform Algorithm
matrix = cv2.getPerspectiveTransform(pts1, pts2)

result = cv2.warpPerspective(result, matrix, (2592, 1944))
cv2.imwrite("/home/pi/testFisheyeTransform.png", result)
result = Image.open("/home/pi/testFisheyeTransform.png")
result = make_square(result)
result = result.save("/home/pi/testFisheyeSquare.png")

img = "/home/pi/testFisheyeSquare.png"
img_out = "/home/pi/testFisheye_corrected.png"
obj = Defisheye(img, dtype=dtype, format=format, fov=fov, pfov=pfov)
obj.convert(img_out)
