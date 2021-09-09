# Python program to illustrate HoughLine 
# method for line detection 
from blur_ar import check_aspect_ratio
import cv2 
import numpy as np 
from imutils import paths
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
args = vars(ap.parse_args())

print(args["image"])
image = cv2.imread(args['image'])

#img = cv2.resize(image,(600,800),interpolation=cv2.INTER_CUBIC)
# Convert the img to grayscale 
gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) 
cv2.imshow("gray",gray)

# Apply edge detection method on the image 
_, thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
cv2.imshow("Tresh",thresh)
ar = check_aspect_ratio(thresh)
text = "Not Blurry"
color = (0,255,0)
if ar > 25 :
	text = "Blurry"
	color = (0,0,255)
cv2.putText(image, "{}: {:.2f}".format(text, ar), (10, 30),
    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 3)
cv2.imshow("final",image)
cv2.waitKey(0)

