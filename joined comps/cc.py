# import the necessary packages
from imutils import paths
import argparse
import matplotlib.pyplot as plt
import numpy as np
import cv2
from scipy import stats as st
from skimage.filters import threshold_sauvola

def check_aspect_ratio(image):
    image1 = image.copy()
    #image = cv2.dilate(image, (3, 3))
    cv2.imshow("bina",image)
    image1 = cv2.cvtColor(image1, cv2.COLOR_GRAY2BGR)
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=4)
    for i in range(2, ret):
        im = labels[labels==i]
        #print("shape",im.shape)
            #self.show_image(image = labels[labels==i])
    widths = []
    heights = []
    c =0
    print("ret",ret)
    print("labels",labels)
    print("stats",stats)
    for stat in stats:
        widths.append(stat[2])
        heights.append(stat[3])

    minh = np.min(heights)
    minw = np.min(widths)
    modew = st.mode(widths).mode
    modeh = st.mode(heights).mode
    for stat in stats:
        w , h = stat[2] , stat[3]
        if (w <= 2*minw  and h > 2*modeh) or (h <= 2*minh and w > 2*modew) :
            #print("(",stat[0],",",stat[1],")")
            #print("(",stat[0]+stat[2],",",stat[1]+stat[3],")")
            image = cv2.rectangle(image1,(stat[0],stat[1]),(stat[0]+stat[2],stat[1]+stat[3]),(0,255,0),2)
            ret =  ret - 1
        else:
            if stat[2]/ stat[3] >= 1.5  :
                image = cv2.rectangle(image1,(stat[0],stat[1]),(stat[0]+stat[2],stat[1]+stat[3]),(0,0,255),2)
                #print(stat[2],"--",stat[3])
                c = c + 1
            else:
                image = cv2.rectangle(image1,(stat[0],stat[1]),(stat[0]+stat[2],stat[1]+stat[3]),(255,0,0),2)
    

    print("centroids",centroids)
    print("modew",modew,"modeh",modeh)
    print("minwidth",minw,"minheight",minh)
    print("ret",ret,"c",c)
    cv2.imshow("final",image)
    return 1

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
ap.add_argument("-mt", "--minthreshold", type=float, default=160.0,
	help="focus measures that fall below this value will be considered 'blurry'")
ap.add_argument("-xt", "--maxthreshold", type=float, default=195.0,
	help="focus measures that fall below this value will be considered 'blurry'")
ap.add_argument("-vt", "--varthreshold", type=float, default=650.0,
	help="focus measures that fall below this value will be considered 'blurry'")
args = vars(ap.parse_args())

print(args["image"])
image = cv2.imread(args['image'])
opname = (args["image"].split('/'))[1]
#print(image.var())
cv2.imshow("original",image)
#image1 = cv2.GaussianBlur(image, (3, 3), 0)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
window_size = 45
thresh = threshold_sauvola(gray, window_size=window_size)
binary = gray < thresh
binary = binary * 255
dist = cv2.convertScaleAbs(binary)
dist1 = cv2.normalize(dist, None, 255,0, cv2.NORM_MINMAX, cv2.CV_8UC1)
cv2.imwrite("op/"+opname,binary)
cv2.imshow("gray",dist1)
ar = check_aspect_ratio(dist1)
text = "not Blurry"
color = (0,255,0)
# if the focus measure is less than the supplied threshold,
# then the image should be considered "blurry"

#print(fm)
# show the image
cv2.putText(image, "{}: {:.2f}".format(text, ar), (10, 30),
    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 3)
#cv2.imshow("Image", image)
key = cv2.waitKey(0)