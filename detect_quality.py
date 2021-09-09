from imutils import paths
import argparse
import numpy as np
import cv2
import math
from skimage.filters import threshold_sauvola

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
    return character_stats


def find_joined_components(stats ,image):
    '''
    This function detects all the joined components by step-by-step exclusion of other small components
    stats - statistics of all smaller to normal sized text components ( i.e. excluding long lines and boxes)
    image - It is the binary of the original image in gray scale
    '''
    draw_image = cv2.cvtColor(image*255, cv2.COLOR_GRAY2BGR) #image to draw boxes for visualising joined comps
    #declaring empty lists for each type
    hyphens = list()
    dots = list()
    other_chars = list()
    joined_comps = list()
    
    for i, stat in enumerate(stats):
        x , y , w , h = stat[0] , stat[1] ,stat[2] , stat[3]
        #detected to be a hyphen if the component has area and width:height ratio falling in the given range
        if ( w*h >= 4 and w*h < 25 ) and ( w/h >= 2.5 and w/h <= 5):
            hyphens.append(i)
        
        #Supposed to be a dot if the area is very less
        #or otherwise if the area is moderately less with lower width:ratio ratio
        #the ratios are selected in a way to satisfy the relation, width = height +- 2px
        elif w*h < 7 or ( w*h <= 12 and w/h<= 2 and w/h >= 0.5) or ( w*h <= 16 and w/h< 1.7 and w/h >= 0.6) :
            dots.append(i)
        
        #Considered to be a joined component - if it exceeds a certain area 
        #and the width is more than twice the height 
        #if the area is less than the specified value, there are chances of it to be any degraded character
        elif ( w/h > 2 and w*h >= 30 ) :
            joined_comps.append(i)
            cv2.rectangle(draw_image,(x,y),(x+w,y+h),(0,0,255),1) 

        #all other valid characters
        else :   
            other_chars.append(i)
    
    #calculating the percentage of joined components
    #we exclude dots from the total 
    joined_comp_factor = (len(joined_comps)/(len(stats)- len(dots)))* 100 if len(stats)-len(dots)!=0 else 0
    
    #printing the statistics
    print("Number of levels (excluding dots) :",len(stats)-len(dots))
    print("Number of joined comps :",len(joined_comps))
    print("Joined comp factor :",joined_comp_factor)
    return joined_comp_factor, draw_image

def find_mask(image,refx,refy):
    '''
    This function creates a mask image
    A completely black image is added with white mask of hexagonal shape at the origin
    The coordinates for this polygon are determined by refx and refy
    refx , refy = reference values for mask creation ( Here, they are the average values of widths and heights )
    image - it is used for creating a total zero pixeled image of same size
    '''
    mask = np.zeros_like(image)
    #calculating 15%, 60% and 75% of the reference values
    px_75 , py_75 = 0.75*refx , 0.75*refy
    px_60 , py_60 = 0.60*refx , 0.60*refy
    px_15 , py_15 = 0.15*refx , 0.15*refy
    #filling the mask image 
    cv2.fillConvexPoly(mask, np.array([[0, 0], [0, py_15], [px_60,py_75],[px_75,py_75],[px_75,py_60],[px_15,0]],dtype=np.int32), (255, 255, 255))
    return mask

def fill_mask(mask,widths,heights):
    '''
    This function is used to fill the white mask region against heights and widths of the components.
    mask - black background image containing white mask to fill
    widths , heights - widths and heights of the components
    '''
    #filling the white mask with black pixels(0 px)
    for w,h in zip(widths,heights):
        mask[w,h] = 0
    return mask

def find_broken_characters(stats,image):
    '''
    This function is used to calculate the broken character factor
    It is done by creating a mask image and then finding the area that is filled
    stats - statistics of all smaller to normal sized text components ( i.e. excluding long lines and boxes)
    image - It is the binary of the original image in gray scale
    '''
    #storing heights and widths from the stats in a different list of their own
    #then calculating the averages which are considered as reference values for mask creation
    widths , heights = np.array(stats)[:,2] , np.array(stats)[:,3]
    refx = math.floor(np.mean(widths))
    refy = math.floor(np.mean(heights))

    #calling a function to create mask
    #then finding the count of all white pixels 
    mask_img = find_mask(image,refx,refy)
    total_mask_area = cv2.countNonZero(mask_img)

    #calling a function to fill the mask region
    #then again finding the count of all white pixels
    #filled pixels count = new black pixel count = old white pixel count - new white pixel count
    mask_fill_img = fill_mask(mask_img.copy(),widths,heights)
    mask_filled_area = total_mask_area - cv2.countNonZero(mask_fill_img)
    
    #finding the percent coverage of white area
    broken_char_factor = (mask_filled_area/total_mask_area) * 100 if total_mask_area!=0 else 0

    #printing the statistics    
    print("reference width :",refx,", Reference height",refy)
    print("Mask filled area :",mask_filled_area,", Total mask area :",total_mask_area)
    print("Broken character factor :",broken_char_factor)

    return broken_char_factor,mask_img,mask_fill_img

def find_white_speckels(stats,image):
    '''
    This funtion is used to find all the white speckels in an image.
    White components with widths and heights less than or equal to 3px are considered to be speckels.
    White speckel factor is used as a factor to determine the extent of touching characters.
    stats - statictics of all the small white components
    image - It is the binary of the original image in gray scale
    '''
    draw_image = cv2.cvtColor(image*255, cv2.COLOR_GRAY2BGR) #image to draw boxes for visualising joined comps
    small_boxes_count = 0 #for storing the count of all mini sized boxes
    
    for stat in stats:
        cv2.rectangle(draw_image,(stat[0],stat[1]),(stat[0]+stat[2],stat[1]+stat[3]),(0,255,0),1) 
        #comparing the widths and heights of each white component
        if stat[2]<=3 and stat[3]<=3 :
            small_boxes_count += 1
            cv2.rectangle(draw_image,(stat[0],stat[1]),(stat[0]+stat[2],stat[1]+stat[3]),(0,0,255),1) 
    
    #finding the percentage of speckel among all the white components
    white_speckel_factor = (small_boxes_count/len(stats))*100 if len(stats)!=0 else 0

    #printing the statistics
    print("Number of Speckels :",small_boxes_count)
    print("Total number of white comps :",len(stats))
    print("White speckel factor :",white_speckel_factor)
    return white_speckel_factor,draw_image

def find_charwise_speckels(characters , noises , image):
    '''
    This function is used to find all the characters having smaller white speckels in them.
    It is an extension of white speckel factor.
    characters - Statictics of all text components
    noises - Statistics of all inner white components within texts
    image - It is the binary of the original image in gray scale
    '''
    draw_image = cv2.cvtColor(image*255, cv2.COLOR_GRAY2BGR) #image to draw boxes for visualising joined comps
    charwise_speckel_count = list(list()) #list used to store the character index with it's speckel count
    speckel_char_count = 0 #Overall count of characters having speckels
    char_count = 0 #character count excluding very small components
    for i,char in enumerate(characters):
        cx1 , cy1 , cx2 , cy2 = char[0] , char[1] , char[0]+char[2] , char[1]+char[3]
        each_count = 0 #to calculate individual speckel count 
        #Only find speckels inside characters having width and height greater than 3px
        if char[2] > 3 and char[3] > 3:
            for noise in noises:
                nx , ny , nw ,nh = noise[0] , noise[1] , noise[2] , noise[3]
                #check if the widths and heights of noises are less than 3px and if the noise is within the character
                if nw <=3 and nh <=3 and nx >= cx1 and ny >= cy1 and nx+nw <= cx2 and ny+nh <=cy2:
                    each_count+=1
                    cv2.rectangle(draw_image,(nx,ny),(nx+nw,ny+nh),(0,0,255),1)

            #count greater than zero indicates that there were speckels in it
            if each_count>0 :
                speckel_char_count += 1
                cv2.rectangle(draw_image,(cx1,cy1),(cx2,cy2),(255,0,0),1)
            char_count += 1
        else:
            each_count = -1
        #append the character index and speckel count
        charwise_speckel_count.append([i,each_count]) 
    
    #find the percentage of characters having speckels
    charwise_speckel_factor = (speckel_char_count/char_count)*100 if char_count!=0 else 0

    #printing the statistics
    print("Number of Characters containing speckels :",speckel_char_count) 
    print("Total number of characters :",len(characters))   
    print("Characters greater than 3px*3px :",char_count)
    print("Character-wise speckel factor :",charwise_speckel_factor)
    return charwise_speckel_factor , draw_image



if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
        help="path to input image")
    ap.add_argument("-v","--visuals", default=False,
        help="To save and display the visuals")
    args = vars(ap.parse_args())

    #reading an image
    print("Input image :",args["image"])
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

    #save the binary image in "output-images" folder
    cv2.imwrite("output-images/"+ output_image_name +"_bin.jpg",binary_disp)
    print("-----------------------------")

    black_comp_stats = find_character_boxes(binary.astype(np.uint8)) #getting statistics of all text characters
    white_noise_stats = find_character_boxes((~binary).astype(np.uint8)) #getting statistics of all inner white components

    #To find joined component factor
    joined_comp_factor , joined_edges_image = find_joined_components(black_comp_stats , binary.astype(np.uint8))
    print("-----------------------------")

    #To find the broken character factor
    broken_char_factor ,mask_image , mask_fill_image = find_broken_characters(black_comp_stats , binary.astype(np.uint8))
    print("-----------------------------")

    #To find the white speckel factor to determine the percent of touching characters
    white_speckel_factor , white_speckel_image = find_white_speckels(white_noise_stats , binary.astype(np.uint8))
    print("-----------------------------")

    #To find the character wise speckel count 
    charwise_speckel_factor , charwise_speckel_image = find_charwise_speckels(black_comp_stats, white_noise_stats,binary.astype(np.uint8))
    print("-----------------------------")
    
    #if True , displays and stores all the images for visual aid
    if args["visuals"]:
        cv2.imshow("joined_edges_image",joined_edges_image)
        cv2.imshow("mask_image",mask_image)
        cv2.imshow("mask_fill_image",mask_fill_image)
        cv2.imshow("charwise_speckel_image",charwise_speckel_image)
        cv2.imshow("white_speckel_image",white_speckel_image)

        cv2.imwrite("output-images/"+ output_image_name +"_joined.jpg",joined_edges_image)
        cv2.imwrite("output-images/"+ output_image_name +"_mask.jpg",mask_image)
        cv2.imwrite("output-images/"+ output_image_name +"_fill.jpg",mask_fill_image)
        cv2.imwrite("output-images/"+ output_image_name +"_charwise_speck.jpg",charwise_speckel_image)
        cv2.imwrite("output-images/"+ output_image_name +"_speckels.jpg",white_speckel_image)
        cv2.waitKey(0)

    