from defisheye import Defisheye

dtype = 'linear'
format = 'fullframe'
fov = 115
pfov = 100

img = "/home/pi/test.jpg"
img_out = "/home/pi/example3_{dtype}_{format}_{pfov}_{fov}.jpg"
obj = Defisheye(img, dtype=dtype, format=format, fov=fov, pfov=pfov)
obj.convert(img_out)
