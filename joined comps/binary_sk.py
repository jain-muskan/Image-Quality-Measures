from blur_ar import check_aspect_ratio
from imutils import paths
import argparse
import matplotlib.pyplot as plt
import numpy as np
import cv2
from scipy import stats as st
from skimage.filters import threshold_sauvola


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
args = vars(ap.parse_args())

print(args["image"])
image = cv2.imread(args['image'])

#image = cv2.resize(image,(900,1580))

opname = (args["image"].split('/'))[-1] if args["image"].find('/') != -1 else args["image"]

opname = opname.split('.')[0]
print(opname)

#print(image.var())
cv2.imshow("original",image)
#image1 = cv2.GaussianBlur(image, (3, 3), 0)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
window_size = 45
#gray = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
thresh = threshold_sauvola(gray, window_size=window_size)
binary = gray < thresh
binary_disp = binary * 255
cv2.imwrite("op/"+ opname +".jpg",binary_disp)

#cv2.imshow("bin",dist1)
deg_perc , dot_perc = check_aspect_ratio(binary.astype(np.uint8))
text = "Not Blurry"
color = (0,255,0)
if deg_perc > 15 or dot_perc > 40:
	text = "Blurry"
	color = (0,0,255)
cv2.putText(image, "{}: {:.2f}".format(text, deg_perc), (10, 30),
    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 3)
cv2.imshow("final",image)
cv2.waitKey(0)