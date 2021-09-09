from imutils import paths
import argparse
import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
from skimage.filters import threshold_sauvola

def check_box_not_empty(stats,x1,y1,x2,y2):
    for stat in stats:
        if stat[1] > y1 and stat[1]+stat[3] < y2 and stat[0] > x1 and stat[0]+stat[2] < x2 :
            return True
    return False

def find_character_boxes(image):
    num_levels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=8)
    character_stats = []
    #declaring empty lists for each type
    for i, stat in enumerate(stats):
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]

        #to indicate long horizontal and vertical lines 
        if ( w/h > 35 and h<6 ) or ( h/w > 25 and w < 6)  :
            pass
    
        #detects huge boxes based on its area and comparatively small boxes if there are any other pixels in it 
        elif w*h >3500 or ( w*h > 1700 and check_box_not_empty(stats,x,y,x+w,y+h)):
            pass

        else:
            character_stats.append(stat)
    return character_stats

def find_speckel_factor(image , characters , noises):
    charwise_speckel_count = []
    speckel_count = 0
    for i,char in enumerate(characters):
        cx1 , cy1 , cx2 , cy2 = char[0] , char[1] , char[0]+char[2] , char[1]+char[3]
        count = 0
        for noise in noises:
            nx , ny , nw ,nh = noise[0] , noise[1] , noise[2] , noise[3]
            if nw <=3 and nh <=3 and nx >= cx1 and ny >= cy1 and nx+nw <= cx2 and ny+nh <=cy2:
                count+=1
                cv2.rectangle(image,(nx,ny),(nx+nw,ny+nh),(0,0,255),1) 

        if count>0 :
            speckel_count += 1
            cv2.rectangle(image,(cx1,cy1),(cx2,cy2),(255,0,0),1)
        charwise_speckel_count.append([i,count])
    
    print(speckel_count,len(charwise_speckel_count),speckel_count/len(characters))    
    return speckel_count/len(characters) , image

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

    black_comp_stats = find_character_boxes(binary.astype(np.uint8))
    white_noise_stats = find_character_boxes((~binary).astype(np.uint8))
    perc , edge_image = find_speckel_factor(image.copy() , black_comp_stats, white_noise_stats)

    cv2.imwrite("output-images/"+ output_image_name +"_edge.jpg",edge_image)

    text = "Good Quality"
    color = (255,0,0)
    if perc >= 0.2 :
        text = "Bad Quality"
        color = (0,0,255)

    cv2.putText(image, "{}: {:.2f}".format(text, perc), (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.imshow("final image",image)

    cv2.waitKey(0)