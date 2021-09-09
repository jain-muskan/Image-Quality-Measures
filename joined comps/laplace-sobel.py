import cv2
from imutils import paths
import argparse
import numpy as np
from matplotlib import pyplot as plt

# loading image
#img0 = cv2.imread('SanFrancisco.jpg',)

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", required=True,
	help="path to input directory of images")
args = vars(ap.parse_args())

for imagePath in paths.list_images(args["images"]):
    # converting to gray scale
    img0 = cv2.imread(imagePath)
    gray = cv2.cvtColor(img0, cv2.COLOR_BGR2GRAY)

    # remove noise
    img = cv2.GaussianBlur(gray,(3,3),0)

    # convolute with proper kernels
    laplacian = cv2.Laplacian(img,cv2.CV_64F)
    sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=3)  # x
    sobely = cv2.Sobel(img,cv2.CV_64F,0,1,ksize=3)  # y
    ero = cv2.erode(img,(3,3))
    canny = cv2.Canny(ero,100,200)

    """ plt.subplot(2,2,1),plt.imshow(img,cmap = 'gray')
    plt.title('Original'), plt.xticks([]), plt.yticks([])
    plt.subplot(2,2,2),plt.imshow(laplacian,cmap = 'gray')
    plt.title('Laplacian'), plt.xticks([]), plt.yticks([])
    plt.subplot(2,2,3),plt.imshow(sobelx,cmap = 'gray')
    plt.title('Sobel X'), plt.xticks([]), plt.yticks([])
    plt.subplot(2,2,4),plt.imshow(sobely,cmap = 'gray')
    plt.title('Sobel Y'), plt.xticks([]), plt.yticks([])

    plt.show() """

    cv2.imshow("original",img0)
    cv2.imshow("blur",img)
    cv2.imshow("laplace",laplacian)
    cv2.imshow("sobelx",sobelx)
    cv2.imshow("sobely",sobely)
    cv2.imshow("canny",canny)
    cv2.waitKey(0)