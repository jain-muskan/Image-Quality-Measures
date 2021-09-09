from imutils import paths
import argparse
import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
from skimage.filters import threshold_sauvola

#to check if there are any pixels in the box
def check_box_not_empty(stats,x1,y1,x2,y2):
    for stat in stats:
        if stat[1] > y1 and stat[1]+stat[3] < y2 and stat[0] > x1 and stat[0]+stat[2] < x2 :
            return True
    return False

def find_small_white_comps(image):
    
    image1 = cv2.cvtColor(image*255, cv2.COLOR_GRAY2BGR) #image to draw boxes for visualising joined comps
    mask = cv2.cvtColor(np.zeros_like(image1),cv2.COLOR_BGR2GRAY)
    num_levels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=8)
    
    count_total_rects = count_small_rects = 0
  
    #declaring empty lists for each type
    for i, stat in enumerate(stats):
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]
        #cv2.rectangle(image1,(x,y),(x+w,y+h),(255,0,0),int(2))
        #to indicate long horizontal and vertical lines 
        if ( w/h > 35 and h<6 ) or ( h/w > 25 and w < 6)  :
            pass
    
        #detects huge boxes based on its area and comparatively small boxes if there are any other pixels in it 
        elif w*h >2500 or ( w*h > 1700 and check_box_not_empty(stats,x,y,x+w,y+h) ):
            pass

        else:
            count_total_rects += 1
            cv2.rectangle(image1,(x,y),(x+w,y+h),(0,255,0),1)
            if w<= 3 and h<=3:
                count_small_rects+=1
                mask[y,x] = 255
                cv2.rectangle(image1,(x,y),(x+w,y+h),(0,0,255),1)

    #print(small_rect_stats)
    cv2.imshow("mask",mask)
    return image1 , mask

def check_box_count(x1,y1,x2,y2,image):
    return cv2.countNonZero(image[y1:y2,x1:x2])
    

def find_speckel_factor(binary , output_image_name):
    drawn_image , mask = find_small_white_comps((~binary).astype(np.uint8))
    cv2.imwrite("output-images/"+ output_image_name +"_dots.jpg",mask)

    image = binary.astype(np.uint8)
    num_levels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=8)

    speckel_present_chars = total_chars = 0
    big_rect_stats = []

    #declaring empty lists for each type
    for i, stat in enumerate(sorted_stats):
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]

        #to indicate long horizontal and vertical lines 
        if ( w/h > 35 and h<6 ) or ( h/w > 25 and w < 6)  :
            pass
    
        #detects huge boxes based on its area and comparatively small boxes if there are any other pixels in it 
        elif w*h >3500 or ( w*h > 1700 and check_box_not_empty(stats,x,y,x+w,y+h) ):
            pass

        else:
            if check_box_count(x,y,x+w,y+h,mask) > 0:
                speckel_present_chars += 1
                cv2.rectangle(drawn_image,(x,y),(x+w,y+h),(255,0,0),1)
                big_rect_stats.append(stat)
            """ else :
                cv2.rectangle(drawn_image,(x,y),(x+w,y+h),(0,255,255),1) """
            total_chars += 1

    cv2.imshow("check",drawn_image)
    cv2.imwrite("output-images/"+ output_image_name +"_edges.jpg",drawn_image)
    print(speckel_present_chars/total_chars)
    return speckel_present_chars/total_chars

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
        help="path to input image")
    args = vars(ap.parse_args())

    print(args["image"])
    image = cv2.imread(args['image'])

    #extracting image name without folder name and extension for later saving purposes
    output_image_name = (args["image"].split('/'))[-1] if args["image"].find('/') != -1 else [args["image"]]
    output_image_name = output_image_name.split('.')[0]

    #converting to gray image and then to binary
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    window_size = 45
    thresh = threshold_sauvola(gray, window_size=window_size)
    binary = gray < thresh
    binary_disp = binary * 255

    #save the binary image in "binary-images" folder
    cv2.imwrite("output-images/"+ output_image_name +"_bin.jpg",binary_disp)

    #calling the check_aspect_ratio function to get the joined component percentage
    perc = find_speckel_factor(binary,output_image_name)

    text = "Good Quality"
    color = (255,0,0)
    if perc >= 0.2 :
        text = "Bad Quality"
        color = (0,0,255)

    cv2.putText(image, "{}: {:.2f}".format(text, perc), (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.imshow("final image",image)

    cv2.waitKey(0)