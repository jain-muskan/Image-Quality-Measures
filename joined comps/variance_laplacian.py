# import the necessary packages
from imutils import paths
import argparse
import matplotlib.pyplot as plt
import numpy as np
import cv2
from skimage.filters import threshold_sauvola


def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
    img = cv2.convertScaleAbs(cv2.Laplacian(image,3))
    hist = cv2.calcHist([np.uint8(np.absolute(img))],[0],None,[256],[0,256])
    """ plt.subplot(121)
    plt.plot(hist)
    plt.subplot(122)
    plt.plot(cv2.calcHist([image],[0],None,[256],[0,256])) """
    #print("hist quantile {}, direct quantile {},max {}, var {},percentile {},mean {}".format(np.quantile(hist,1.0),np.quantile(img,0.9),np.max(img),img.var(),np.percentile(hist,99),np.mean(img)))
    #print("width {},height {},area{} , div{}".format(w,h,w*h,np.quantile(hist,0.99)/(w*h)))
    #plt.show() 
    print("max",np.max(img))
    print("var",np.var(img))
    print("mean",np.mean(img))
    return np.max(img),np.var(img)


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", required=True,
	help="path to input directory of images")
ap.add_argument("-mt", "--minthreshold", type=float, default=160.0,
	help="focus measures that fall below this value will be considered 'blurry'")
ap.add_argument("-xt", "--maxthreshold", type=float, default=195.0,
	help="focus measures that fall below this value will be considered 'blurry'")
ap.add_argument("-vt", "--varthreshold", type=float, default=650.0,
	help="focus measures that fall below this value will be considered 'blurry'")
args = vars(ap.parse_args())

i = 0
for imagePath in paths.list_images(args["images"]):
    # load the image, convert it to grayscale, and compute the
    # focus measure of the image using the Variance of Laplacian
    # method
    image = cv2.imread(imagePath)
    #print(image.var())
    cv2.imshow("original",image)
    #image1 = cv2.GaussianBlur(image, (3, 3), 0)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    window_size = 45
    thresh = threshold_sauvola(gray, window_size=window_size)
    binary = gray < thresh
    cv2.imwrite("op/img"+str(i)+".jpg",binary*255)
    print(i)
    #cv2.imshow("gray",gray)
    image =  cv2.imread("op/img"+str(i)+".jpg")
    fm , fv = variance_of_laplacian(gray)
    text = "not Blurry"
    color = (0,255,0)
    # if the focus measure is less than the supplied threshold,
    # then the image should be considered "blurry"
    if fm < args["minthreshold"]:
        text = "Blurry"
        color = (0,0,255)
    elif fm > args["minthreshold"] and fm < args["maxthreshold"] and fv < args["varthreshold"] :
        text = "Blurry"
        color = (0,0,255)

    #print(fm)
    # show the image
    cv2.putText(image, "{}: {:.2f}".format(text, fm), (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 3)
    cv2.imshow("Image", image)
    key = cv2.waitKey(0)
    i = i+1