# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import math
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import cv2

# Fixing random state for reproducibility
def show_hist(stats,x,y,indices,image):

    avgx = math.ceil(np.mean(x))
    avgy = math.ceil(np.mean(y))
    maxX = math.ceil(np.max(x))
    maxY = math.ceil(np.max(y))
    print("Avg x and y :",avgx,avgy)
    print("Max x and y :",maxX,maxY)

    total_area = total_reference_area = broken_char_area = 0
    for i in range(len(x)):
        xe , ye , index = x[i] , y[i] , indices[i]
        total_area +=xe*ye
        #cv2.rectangle(image,(stats[index][0],stats[index][1]),(stats[index][0]+xe,stats[index][1]+ye),(0,255,255),1)
        if xe <= avgx  and ye<= avgy:
            total_reference_area += xe*ye
            cv2.rectangle(image,(stats[index][0],stats[index][1]),(stats[index][0]+xe,stats[index][1]+ye),(255,0,0),1)

        if xe > 0 and ye > 0 and xe <= 0.75*avgx and ye <= 0.75*avgy  :#and ye/avgy - xe/avgx <= 0.15 and xe/avgx - ye/avgy <= 0.15
            broken_char_area += xe * ye 
            cv2.rectangle(image,(stats[index][0],stats[index][1]),(stats[index][0]+xe,stats[index][1]+ye),(0,0,255),1)
     
    
    print("Direct calculation",broken_char_area,total_reference_area,total_area,broken_char_area/total_reference_area)
    
    total_reference_area = broken_char_area = 0
    binx = biny = 100
    
    hist, xedges, yedges,_ = plt.hist2d(x, y,bins=[binx,biny],range=[[0, avgx], [0, avgy]],norm = colors.LogNorm(),cmap="brg")

    for i in range(1,binx):
        for j in range(1,biny):
            if hist[i][j] != 0 :
                if i<= 0.75*binx and j <=0.75*biny : #and j-i <= 15 and i - j <= 15
                    broken_char_area += i*j *hist[i][j]
                total_reference_area += i*j*hist[i][j]
    #ax1.set_facecolor((1.0, 1.0, 1.0))
    print("Through Histogram " + str(binx)+" x "+str(biny),broken_char_area,total_reference_area,broken_char_area/total_reference_area)    

    """ print(hist)
    print(xedges)
    print(yedges) """
    cv2.imshow("image",image)
    
    #plt.hist2d()
    #plt.hist2d(x,y,bins=100,range=[[0,avgx],[0,avgy]],color="white")
    #ax1.imshow(hist,origin='low')
    
    plt.xlabel('width')
    plt.ylabel('height')
    plt.colorbar()
   # plt.patch.set_facecolor('white')

    plt.show()
    cv2.waitKey(0)
    return image