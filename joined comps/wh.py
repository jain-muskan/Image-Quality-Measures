from imutils import paths
import argparse
import matplotlib.pyplot as plt
import numpy as np
import cv2
from scipy import stats as st

def check_aspect_ratio(image):
    print(image.shape)
    print(type(image[0][0]))
    #image1 = image.copy()
    imgh , imgw = image.shape
    cv2.imshow("img",image)
    image1 = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=4)
    
    widths = []
    heights = []
    c =0
    print("ret",ret)
    print("labels",labels)
    print("stats",stats)
    ul = int(0.95*len(stats))
    for stat in stats[1:]:
        widths.append(stat[2])
        heights.append(stat[3])

    minh = np.min(heights) if np.min(heights) > 3 else 3 
    minw = np.min(widths) if np.min(widths) > 3 else 3
    #minw , minh = np.min(widths) , np.min(heights) 
    #modew , modeh= st.mode(widths).mode , st.mode(heights).mode
    modeh = st.mode(heights).mode if st.mode(heights).mode > 5 else 5 
    modew = st.mode(widths).mode if st.mode(widths).mode > 5 else 5

    for stat in stats[1:]:
        w , h = stat[2] , stat[3]
        if h> 0.6*imgh or w> 0.6*imgw or (w <= minw  and h > 2*modeh) or (h <= minh and w > 2*modew)  :
            #print("(",stat[0],",",stat[1],")")
            #print("(",stat[0]+stat[2],",",stat[1]+stat[3],")")
            image = cv2.rectangle(image1,(stat[0],stat[1]),(stat[0]+stat[2],stat[1]+stat[3]),(0,255,0),2)
            ret =  ret - 1
        elif (w/h <= 1 or h/w <=1) and w<=minw and h<=minh:
            ret = ret - 1
        else:
            if w/ h >= 1.7  :
                image = cv2.rectangle(image1,(stat[0],stat[1]),(stat[0]+stat[2],stat[1]+stat[3]),(0,0,255),2)
                #print(stat[2],"--",stat[3])
                c = c + 1
            else :   
                image = cv2.rectangle(image1,(stat[0],stat[1]),(stat[0]+stat[2],stat[1]+stat[3]),(255,0,0),2)
    

    print("centroids",centroids)
    print("modew",modew,"modeh",modeh)
    print("minwidth",minw,"minheight",minh)
    print("ret",ret,"c",c,c/ret)
    print(image.shape)
    cv2.imshow("final",image)
    cv2.waitKey(0)
    return (c/ret)*100