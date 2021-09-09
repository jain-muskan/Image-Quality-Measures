from imutils import paths
import argparse
import numpy as np
import cv2
from skimage.filters import threshold_sauvola

#to check if there are any pixels in the box
def check_box_not_empty(stats,x1,y1,x2,y2):
    for stat in stats:
        if stat[1] > y1 and stat[1]+stat[3] < y2 and stat[0] > x1 and stat[0]+stat[2] < x2 :
            return True
    return False

def check_aspect_ratio(image,output_image_name):
    
    imgh , imgw = image.shape
    draw_image = cv2.cvtColor(image*255, cv2.COLOR_GRAY2BGR) #image to draw boxes for visualising joined comps
    
    num_levels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=4)
    
    #declaring empty lists for each type
    valid_chars = []
    long_lines = []
    joined_comps = []
    huge_boxes = [] 
    dots = []
    hyphens = []
    
    #sorting the "stats" array based on increasing order of heights ( fourth column of stats)
    sorted_stats = stats[np.argsort(stats[:, 3])]

    for i, stat in enumerate(sorted_stats):
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]

        #to indicate long horizontal and vertical lines 
        if ( w/h > 35 and h<6 ) or ( h/w > 25 and w < 6)  :
            long_lines.append(i)
    
        #detects huge boxes based on its area and comparatively small boxes if there are any other pixels in it 
        elif w*h >2500 or ( w*h > 1700 and check_box_not_empty(sorted_stats[i:],x,y,x+w,y+h) ):
            huge_boxes.append(i)
        
        #tracing hyphens
        elif w*h >= 4 and w*h < 25 and w/h >= 2.5 and w/h <= 5:
            hyphens.append(i)
        
        #tracing dots and tiny disturbances 
        elif w*h < 7 or ( w*h <= 12 and w/h<= 2 and w/h >= 0.5) or ( w*h <= 16 and w/h< 1.7 and w/h >= 0.6) :
            dots.append(i)
        
        #finding joined components - if the width is more than 2 times the height and exceeds certain area
        #if the area is less than that, there are chances of it to be any degraded character
        elif ( w/h > 2 and w*h >= 25 ) :
            
            joined_comps.append(i)

        #all other valid characters
        else :   
            valid_chars.append(i)

        image = cv2.rectangle(draw_image,(x,y),(x+w,y+h),(0,0,255),2)
    #display and save the "draw_image" in "output-images" folder
    cv2.imshow("drawn image",draw_image)
    cv2.imwrite("output-images/"+output_image_name +".jpg",draw_image) 
    
    #printing the statistcis
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

    return (len(joined_comps)/(len(stats)- len(dots)))* 100  #return joined component %


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
    cv2.imwrite("binary-images/bin_"+ output_image_name +".jpg",binary_disp)

    #calling the check_aspect_ratio function to get the joined component percentage
    joined_perc = check_aspect_ratio(binary.astype(np.uint8),output_image_name)
    text = "Not Blurry"
    color = (0,255,0)
    if joined_perc > 15 :
        text = "Blurry"
        color = (0,0,255)

    cv2.putText(image, "{}: {:.2f}".format(text, joined_perc), (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 3)
    cv2.imshow("final image",image)
    cv2.waitKey(0)