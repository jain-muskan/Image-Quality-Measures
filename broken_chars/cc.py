from imutils import paths
import argparse
import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
from skimage.filters import threshold_sauvola
from mask import find_mask,fill_mask

#to check if there are any pixels in the box
def check_box_not_empty(stats,x1,y1,x2,y2):
    for stat in stats:
        if stat[1] > y1 and stat[1]+stat[3] < y2 and stat[0] > x1 and stat[0]+stat[2] < x2 :
            return True
    return False

def find_mask_percentage(image,output_image_name):
    
    imgh , imgw = image.shape
    image1 = cv2.cvtColor(image*255, cv2.COLOR_GRAY2BGR) #image to draw boxes for visualising joined comps

    num_levels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=8)
    widths = []
    heights = []
    indices = []
    sorted_stats = stats[np.argsort(stats[:, 3])]
    #declaring empty lists for each type
    for i, stat in enumerate(sorted_stats):
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]
        #to indicate long horizontal and vertical lines 
        if ( w/h > 35 and h<6 ) or ( h/w > 25 and w < 6)  :
            pass
    
        #detects huge boxes based on its area and comparatively small boxes if there are any other pixels in it 
        elif w*h >2500 or ( w*h > 1700 and check_box_not_empty(sorted_stats[i:],x,y,x+w,y+h) ):
            pass

        else:
            heights.append(w)
            widths.append(h)
            indices.append(i)
            #cv2.rectangle(draw_image,(x,y),(x+w,y+h),(0,0,255),1)
    cv2.imshow("edges",image1)
    refx = math.floor(np.mean(widths))
    refy = math.floor(np.mean(heights))

    print("reference width :",refx,", Reference height",refy)

    mask_img = cv2.cvtColor(find_mask(image1,refx,refy),cv2.COLOR_BGR2GRAY)
    cv2.imwrite("output-images/"+ output_image_name +"_mask.jpg",mask_img)
    total_mask_area = cv2.countNonZero(mask_img)

    mask_fill_img = fill_mask(mask_img,widths,heights)
    cv2.imwrite("output-images/"+ output_image_name +"_fill.jpg",mask_fill_img)
    mask_filled_area = total_mask_area - cv2.countNonZero(mask_fill_img)

    print("Mask filled area :",mask_filled_area,", Total mask area :",total_mask_area)
    print("BSF :",mask_filled_area/total_mask_area)
    return (mask_filled_area/total_mask_area)*100


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
    perc = find_mask_percentage(binary.astype(np.uint8),output_image_name)
    text = "Good Quality"
    color = (255,0,0)
    if perc > 50 :
        text = "Bad Quality"
        color = (0,0,255)

    cv2.putText(image, "{}: {:.2f}".format(text, perc), (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.imshow("final image",image)

    cv2.waitKey(0)