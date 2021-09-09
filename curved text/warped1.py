import numpy as np
from imutils import paths
import argparse
import cv2
import math
from skimage.filters import threshold_sauvola
from skimage.morphology import skeletonize, thin

def find_character_boxes(image):
    '''
    This funtion finds all the connected components in an image.
    It then excludes lines and big boxes.
    image - It is the binary of the original image in gray scale
    '''
    #This function finds white coloured components
    #So, if black background -  detects text characters and lines
    #white background - detects small holes and spaces within characters
    num_levels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=8)
    imgh , imgw = image.shape

    character_stats = list() #to store the statistics excluding lines and boxes
    for i, stat in enumerate(stats):
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]

        #to indicate long horizontal and vertical lines 
        if ( w/h > 35 and h<6 ) or ( h/w > 25 and w < 6)  :
            pass
    
        #detects huge boxes and very small boxes directly based on its area 
        elif w*h > 0.5*imgh*imgw or w*h < 30 or ( w*h>7000 and w/h > 3 ):#
            pass
        
        #all other components 
        else:
            character_stats.append(stat)
    return character_stats

def find_angle(image):
    '''
    This function is used to find the slope i.e. angle of inclination of the text within the given image portion.
    If more than one contour is detected , the slope of contour having the maximum area is considered.
    image - some section of the original image where a connected component was found
    '''
    contours, hierarchy = cv2.findContours(image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    max_area , final_angle , max_cnt = -1 , 0 , list() #initialisation

    for cnt in contours:
        #we fit a line in those contour coordinates and then find the slope of it
        #it is then coverted to angle in degrees
        vx , vy , x , y = cv2.fitLine(cnt, cv2.DIST_L2,0,0.01,0.01)[:,0]
        slope = vy/vx
        angle = abs((math.atan2(vy,vx)*180)/3.14)

        #findng the area of rectangle surrounding the contour
        #check if the new area is the maximum area, if yes, then change the respective values
        _,_,w,h = cv2.boundingRect(cnt)
        if w*h > max_area:
            max_area = w*h
            final_angle = angle
            max_cnt = cnt

    print("Max area :",max_area,"  Slope :",final_angle,"  If slant :",final_angle> 10 and final_angle<80)
    return final_angle
        

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
        help="path to input image")
    args = vars(ap.parse_args())

    print(args["image"])
    image = cv2.imread(args['image'])
    rows,cols = image.shape[:2]

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
    
    #dilation
    diameter_dial = 7
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(diameter_dial,diameter_dial))
    dilation = cv2.dilate(binary.astype(np.uint8)*255,kernel,iterations = 1)
    cv2.imshow("dilate",dilation)

    #erosion
    diameter_ero = 7
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(diameter_ero,diameter_ero))
    erosion = cv2.erode(dilation,kernel,iterations = 1)
    cv2.imshow("erode",erosion)

    #skeletonise
    skeleton = skeletonize(erosion,method='lee')
    cv2.imshow("skeleton",skeleton.astype(np.uint8))
    cv2.imwrite("output-images/"+ output_image_name +"_skel.jpg",skeleton)
    cv2.imshow("final curve",~skeleton.astype(np.uint8))
    cv2.imwrite("output-images/"+ output_image_name +"_invert_skel.jpg",~skeleton)

    #alternative to skeletonise - thinning with 12 iterations
    #we are not using it's result further
    thinning = thin(erosion,max_iter=12)
    cv2.imshow("thin",thinning.astype(np.uint8)*255)

    #finds connected components in the eroded image
    #For every connected component found , we send only that portion of the skeletonized image
    #to find_angle() which then returns the angle of inclination of text in that component
    component_stats = find_character_boxes(erosion)
    text_angles = [] #to store all the component indices along with their angles
    slant_text_count = 0 #count the number of components having inclined text
    vr_image = image.copy() #image for visualisation purpose

    for i,stat in enumerate(component_stats):
        x1 , y1 , x2 , y2 = stat[0] , stat[1] ,stat[0]+stat[2] , stat[1]+stat[3]
        angle  = find_angle(skeleton[y1:y2,x1:x2]) 
        text_angles.append([i,angle]) #appending the new index value of component along with the angle
        if angle > 10 and angle < 80 :
            slant_text_count += 1
            cv2.rectangle(vr_image,(x1,y1),(x2,y2),(0,0,255),2)
        else :
            cv2.rectangle(vr_image,(x1,y1),(x2,y2),(0,255,0),2)

    cv2.imshow("components",vr_image)
    print(text_angles)
    


    cv2.waitKey(0)