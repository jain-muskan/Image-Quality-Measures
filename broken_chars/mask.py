import cv2
import numpy as np
from imutils import paths
import argparse
import math

def find_mask(image,refx,refy):

    mask = np.zeros_like(image)
    imgh,imgw,_ = image.shape
    print(imgh,imgw,imgh*imgw)
    print(mask.dtype)

    px_75 , py_75 = 0.75*refx , 0.75*refy
    px_60 , py_60 = 0.60*refx , 0.60*refy
    px_15 , py_15 = 0.15*refx , 0.15*refy
    cv2.fillConvexPoly(mask, np.array([[0, 0], [0, py_15], [px_60,py_75],[px_75,py_75],[px_75,py_60],[px_15,0]],dtype=np.int32), (255, 255, 255))
    cv2.imshow("mask",mask)
    return mask

def fill_mask(image,widths,heights):
    for w,h in zip(widths,heights):
        image[h,w] = 0
    cv2.imshow("plotted",image)
    return image