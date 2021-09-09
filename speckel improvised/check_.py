import cv2
import numpy as np
from imutils import paths
import argparse
import math

image = cv2.imread("inputs\image1.jpg")

mask = cv2.cvtColor(np.zeros_like(image),cv2.COLOR_BGR2GRAY)
print(mask)
imgh,imgw,_ = image.shape
print(imgh,imgw,imgh*imgw)
for j in range(200):
    for i in range(100):
        mask[j,i] = 255
cv2.imshow("mask1",mask[0:600,0:200])
print(mask.dtype)
print(mask.shape)
cv2.imshow("mask",mask)
cv2.waitKey(0)
