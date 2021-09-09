import numpy as np
from imutils import paths
import argparse
import cv2
import math
from skimage.filters import threshold_sauvola
from skimage.morphology import skeletonize, thin

def check_box_not_empty(stats,x1,y1,x2,y2):
    '''
    This function checks if there are any smaller boxes in a bigger box.
    stats - statistics of all the boxes.
    x1,y1,x2,y2 - Top left and bottom right edges of the bigger box.
    '''
    for stat in stats:
        if stat[1] > y1 and stat[1]+stat[3] < y2 and stat[0] > x1 and stat[0]+stat[2] < x2 :
            return True
    return False

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

    character_stats = list() #to store the statistics excluding lines and boxes
    for i, stat in enumerate(stats):
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]

        #to indicate long horizontal and vertical lines 
        if ( w/h > 35 and h<6 ) or ( h/w > 25 and w < 6)  :
            pass
    
        #detects huge boxes directly based on its area 
        #Classsifies components as small boxes if there are any other components(character) in it
        #If no boxes,then it is a big text or a long one 
        elif w*h >3000 or ( w*h > 1700 and check_box_not_empty(stats,x,y,x+w,y+h)):
            pass
        
        #all other components 
        else:
            character_stats.append(stat)
    return stats

def find_width_height(box):
    w , h = abs(box[0][0]-box[3][0]) , abs(box[0][1]-box[3][1])
    for i in range(3):
        w = abs(box[i][0] - box[i+1][0]) if abs(box[i][0] - box[i+1][0])>w else w
        h = abs(box[i][1] - box[i+1][1]) if abs(box[i][1] - box[i+1][1])>h else h
    return w,h

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
    
    #print(avgx,avgy)
    diameter_dial = 7
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(diameter_dial,diameter_dial))
    dilation = cv2.dilate(binary.astype(np.uint8)*255,kernel,iterations = 1)
    cv2.imshow("dilate",dilation)
    diameter_ero = 7
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(diameter_ero,diameter_ero))
    erosion = cv2.erode(dilation,kernel,iterations = 1)
    cv2.imshow("erode",erosion)

    """ img1 =  image.copy()    
    contours, hierarchy = cv2.findContours(erosion,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        img1 = cv2.drawContours(img1, [cnt], -1, (0,0,255), 2)
    cv2.imshow("img1",img1) """

    black_comp_stats = find_character_boxes(erosion)

    widths , heights = np.array(black_comp_stats)[:,2] , np.array(black_comp_stats)[:,3]
    avgx = math.floor(np.mean(widths))
    avgy = math.floor(np.mean(heights))
    dr = image.copy()
    for stat in black_comp_stats:
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]
        cv2.rectangle(dr,(x,y),(x+w,y+h),(255,0,0),2)
    cv2.imshow("dr",dr)

    skeleton = skeletonize(erosion,method='lee')
    cv2.imshow("skeleton",skeleton.astype(np.uint8))

    thinning = thin(erosion,max_iter=15)
    cv2.imshow("thin",thinning.astype(np.uint8)*255)


    cv2.imwrite("output-images/"+ output_image_name +"_edge.jpg",skeleton)
    contours, hierarchy = cv2.findContours(skeleton,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)    
    
    cv2.imshow("final curve",~skeleton.astype(np.uint8))
    cv2.imwrite("output-images/"+ output_image_name +"_final.jpg",~skeleton)

    img = image.copy()
    curved = 0
    for cnt in contours:
        vx , vy , x1 , y1 = cv2.fitLine(cnt, cv2.DIST_L2,0,0.01,0.01)[:,0]

        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        
        w , h = find_width_height(box)
        w ,h  = w if w!=0 else 1 , h if h!=0 else 1 
        area = cv2.contourArea(box)
        
        """ x2,y2,w,h = cv2.boundingRect(cnt)
        img = cv2.rectangle(img,(x2,y2),(x2+w,y2+h),(255,0,0),2) """

        if (area > 15 and area < 3000 and ( w/h < 0.8 or w/h >1.2) ) or (area >= 3000 and w/h > 5.5)  : #and not ( w/h < 2 and w*h > 200)
            slope = vy/vx
            slope = (math.atan2(vy,vx)*180)/3.14
            #print(w*h , w , h , w/h)
            print("slope :",slope)
            
            if abs(slope) < 10 or abs(slope)>80 :
                """ print(box)
                print(area , w , h )
                print("straight", abs(slope)) """
                img = cv2.drawContours(img, [box], -1, (0,255,0), 2)
                #img = cv2.line(img,(cols-1,righty),(0,lefty),(0,0,255),2)
            else :
                """ print("curved", abs(slope))
                print(box)
                print(area , w , h ) """
                #img = cv2.line(img,(cols-1,righty),(0,lefty),(0,0,255),2)
                img = cv2.drawContours(img, [box], -1, (0,0,255), 2)
                curved += 1
        else:
            img = cv2.drawContours(img,[box],0,(255,0,255),2)

    print(curved,len(contours))
    cv2.imshow("contours",img)
    cv2.imwrite("output-images/"+ output_image_name +"_cont.jpg",img)


    cv2.waitKey(0)