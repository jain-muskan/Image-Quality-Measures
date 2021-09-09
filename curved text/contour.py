import numpy as np
from imutils import paths
import argparse
import cv2
import math
from skimage.filters import threshold_sauvola

def find_angles(cordinates):
    coords = cordinates.tolist()
    l = len(coords)
    coords.append(coords[0])
    #print(coords)
    count = 0
    for c in range(l):
        x1 , y1 ,x2 , y2 = coords[c][0][0] , coords[c][0][1] , coords[c+1][0][0] , coords[c+1][0][1]
        slope = abs((y2-y1)/ (x2-x1)) if x2-x1>0 else 9999
        deg =  math.degrees(math.atan(slope))
        print(x1,y1,"--",x2,y2,"=",deg)
        if deg > 15 and deg < 80 :
            count += 1
    print(l,count)
    if count > 0.4*l :
        print("True")
        return True
    return False


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
help="path to input image")
args = vars(ap.parse_args())


input_img = args["image"]
im = cv2.imread(input_img)
output_image_name = (input_img.split('/'))[-1] if input_img.find('/') != -1 else [input_img]
output_image_name = output_image_name.split('.')[0]
gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray,(5,5),0)
cv2.imshow("blur",gray)
window_size = 45
thresh = threshold_sauvola(gray, window_size=window_size)
binary = gray < thresh
binary_disp = binary.astype(np.uint8) * 255
im2 = im.copy()
kernel = np.ones((7,7),np.uint8)
dilate = cv2.dilate(binary_disp,kernel)
cv2.imshow("dilated",dilate)
#save the binary image in "binary-images" folder
cv2.imshow("binary",binary_disp)
num_levels, labels, stats, centroids = cv2.connectedComponentsWithStats(dilate, connectivity=4)

for i, stat in enumerate(stats):
    x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]
    #print(x,y,x+w,y+h)
    cv2.rectangle(im2,(x,y),(x+w,y+h),(255,0,0),1)
#print(centroids)
for c in centroids:
    x , y = int(round(c[0])) , int(round(c[1]))
    cv2.line(im2,(x,y),(x,y),(0,0,255),4)

cv2.imshow("con",im2)
cv2.imwrite("outputs/"+output_image_name+".jpg",im2)
contours, hierarchy = cv2.findContours(dilate ,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
for cnt in contours:
    epsilon = 0.009*cv2.arcLength(cnt,True)
    approx = cv2.approxPolyDP(cnt,epsilon,True)
    approx=cv2.convexHull(approx)
    
    #print("hyi",approx)
    if cv2.contourArea(approx) > 150:
        print(cv2.contourArea(approx))
        im = cv2.drawContours(im,[approx],0,(255,0,0),1)
        if find_angles(approx):
            print(cv2.contourArea(approx))
            im = cv2.drawContours(im,[approx],0,(0,0,255),1)
cv2.imwrite("outputs/"+output_image_name+"_cont.jpg",im)
cv2.imshow("image",im)
cv2.waitKey(0)