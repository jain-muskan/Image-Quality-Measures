from imutils import paths
import argparse
import matplotlib.pyplot as plt
import numpy as np
import cv2


def check_box_not_empty(stats,x1,y1,x2,y2):
    for stat in stats:
        if stat[1] > y1 and stat[1]+stat[3] < y2 and stat[0] > x1 and stat[0]+stat[2] < x2 :
            return True
    return False

def check_aspect_ratio(image):
    #print(image.shape)
    img = image.copy()
    #print(type(image[0][0]))

    imgh , imgw = image.shape
    cv2.imshow("img",image)

    """ for i in range(imgh):
        for j in range(imgw):
            if image[i][j]> 0 and image[i,j] >120:
                print(i,j,image[i,j]) """

    image1 = cv2.cvtColor(image*255, cv2.COLOR_GRAY2BGR)
    
    num_levels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=4)
    #print(num_levels , len(labels),len(stats))
    valid_chars = []
    long_lines = []
    joined_comps = []
    huge_boxes = [] 
    dots = []
    hyphens = []
    #print("labels",labels)

    #print("stats",stats)  
    sorted_stats = stats[np.argsort(stats[:, 3])]
    #print(sorted_stats)

    for i, stat in enumerate(sorted_stats):
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]

        if ( w/h > 35 and h<6 ) or ( h/w > 25 and w < 6)  :
            #image = cv2.rectangle(image1,(x,y),(x+w,y+h),(0,255,255),1)
            long_lines.append(i)
            #print(w,h,w*h,h/w)
    
        elif w*h >2500 or ( w*h > 1700 and check_box_not_empty(sorted_stats[i:],x,y,x+w,y+h) ):
            #image = cv2.rectangle(image1,(x,y),(x+w,y+h),(0,255,0),2)
            huge_boxes.append(i)
        
        elif w*h >= 4 and w*h < 25 and w/h >= 2.5 and w/h < 5:
            #image = cv2.rectangle(image1,(x,y),(x+w,y+h),(255,255,0),2)
            hyphens.append(i)
            #print("hypehn",w,h,w/h,h/w,w*h)
        
        elif w*h < 7 or ( w*h <= 12 and w/h<= 2 and w/h >= 0.5) or ( w*h <= 16 and w/h< 1.7 and w/h >= 0.6) :
            #image = cv2.rectangle(image1,(x,y),(x+w,y+h),(255,255,255),1)
            dots.append(i)
            #print("dot",w,h,w*h,w/h,h/w)
            """ k = stat[1]+h//2
            n = stat[0]+ w//2
            print("pixel",img[k,n]) """
        
        elif ( w/h > 2 and w*h >= 25 ) :
            image = cv2.rectangle(image1,(x,y),(x+w,y+h),(0,0,255),1)
            joined_comps.append(i)
            #print(w,h,w*h,w/h,h/w)

        else :   
            #image = cv2.rectangle(image1,(x,y),(x+w,y+h),(255,0,0),2)
            valid_chars.append(i)
            #print(w,h,w/h,h/w,h*w,area)
            #print(w,h,w*h,w/h,h/w)
        #print(w,h,w*h,w/h,h/w)
        """ if h/w >= 3 :
            vertc = vertc + 1 """
            #image = cv2.rectangle(image1,(x,y),(x+w,y+h),(255,255,255),2)

        k = stat[1]+h//2
        n = stat[0]+ w//2
        #print("pixel",img[k,n])
        #print("pixel",image[stat[1]+h//2,stat[0]+ w//2])
    #print("centroids",centroids)

    cv2.imwrite("test2/image1.jpg",image1)
    print("Total :",len(long_lines)+len(huge_boxes)+len(hyphens)+len(dots)+len(joined_comps)+len(valid_chars))
    print("Number of levels :",len(stats))
    print("Number of boxes :",len(huge_boxes))
    print("Number of lines :",len(long_lines))
    print("Number of hyphens :",len(hyphens))
    print("Number of valid chars :",len(valid_chars))
    print("Number of dots :",len(dots))
    print("Number of joined comps :",len(joined_comps))
    print("Total - dots :",len(stats)-len(dots))
    
    print("Joined comp % (Total-dots) :",(len(joined_comps)/(len(stats)- len(dots)))* 100,"%")
    print("Dots % Total :", (len(dots)/len(stats))*100,"%")

    cv2.imshow("final",image)
    cv2.waitKey(0)
    return (len(joined_comps)/(len(stats)- len(dots)))* 100 , (len(dots)/len(stats))*100

