
#Program: At the moment this program is set to detect any object that is green. So don't wear green, unless you want to detect yourself.

#Features:

#1) Tracking:

        # - Program takes every frame and turns it into an hsv image (hue, saturation, value) and that allows the program to
            #filter out any object within the range of the specified color and a mask is created.

        # - Once the object is filtered out, noise is removed from the mask, this removes any imperfections. And then any holes
            #inside of the mask is filled in, this gives us a perfect mask of the image.

        # - Original frame is then overlayed ontop of the mask, so the objects with that specified color is shown and everything else is black.

        # - Contours on the mask are found and they are then traced on the original frame.

        # - Center of the contour is calculated as x & y coordinates and its marked on the original frame.

        # - This center is what allows me to know where my object is on the screen, thus allowing me to control the game.


#2) Other features:
        
        # - The program allows you to press space and that will take a screenshot of the current frame and that screenshot is displayed.

        # - The program then allows you to select a region of interest(roi) by selecting a box on the snapshot.

        # - If you press ENTER, that region is isolated from the snapshot and displayed on a seperate window.
        

        # - This feature is meant to be used to allow the user to select any object they want and then my program will analyze the roi
            #and the average color will be calculated.

        # - This average will then be used to calculate lower and upper bounds for the color of that object and it will be detected.

        # - The tracking features listed above will be implemented. 


        # THIS DOES NOT WORK AT THE MOMENT, as there is a problem with running through the roi and analyzing the colors.






#Libraries are imported  
import cv2
import numpy as np
import colorsys




#lower and upper bounds are set for the current color, so the program is still able to detect the object
# across different light conditions.

#In this case, green is being detected. 
lowerBound = np.array([33,80,40])
upperBound = np.array([102,255,255])


#Camera feed is captured from main camera
cam = cv2.VideoCapture(0)



#Main loop that keeps running to recieve the frames and handle them.
while True:

    #Current frame is read
    ret, img=cam.read()

    
    #Convert BGR to HSV
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


    #Create mask, which only has the color of the object that is being detected
    mask = cv2.inRange(imgHSV, lowerBound, upperBound)



    #parameters for removing noise are set
    kernelOpen = np.ones((5,5))
    kernelClose = np.ones((5,5))


    #Imperfections in the mask are removed
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen) #Removes useless noise
    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose) #Fills in any holes in mask


    #Combines mask with the original frame so only the object is being shown while everything else is black.
    overlay = cv2.bitwise_and(img,img, mask= maskClose)


    
    #Contours are found and outlined
    _,contours,_ = cv2.findContours(maskClose, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Finds the points of contours
    cv2.drawContours(img, contours, -1, (255,255,255), 3)   #Draws contours around those points


    #Loop finds center of contours
    for c in contours:
        
        # compute the center of the contour
        M = cv2.moments(c) # Finds different characteristics about each contour, such as area, center, etc..


        #This extracts only the center of the contour and gives us an X any Y coordinate of the center.
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        

        #Creates circle at the center of the contour
        cv2.circle(img, (cX, cY), 7, (255, 255, 255), -1)
        cv2.putText(img, "center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)



        #Condition statement sees if tracked object is on right or left or screen
        if cX < 300:
            print "right"

        else:
            print "left"

            
    #Feature that allows user to select any object they want.
    #This will not analyze the color of the selected part as that causes a crash if it is kept in the code.


    #Pressing space will allow you to take a snapshot, then selecting a roi and pressing enter will display the roi.
    if cv2.waitKey(1) == 32:
        
        showCrosshair = False
        x0, y0, y1, x1 = cv2.selectROI("snapshot", img, showCrosshair)#selects roi(region of interest) and gives us the x and y coordinates of rectangle
        
        croppedImg = img[y0:y0+y1 , x0:x0+x1] #roi is selected from snapshot

        #height and width are calculated
        height = y0 - y1
        width = x0 - x1
                
        cv2.imshow("croppedImg", croppedImg)



    #Different frames are displayed
    cv2.imshow('camera', img) #displays original frame with contours 
    cv2.imshow('HSV', imgHSV) #displays hsv frame
    cv2.imshow('mask&image Overlay', overlay) #displays mask 



    #If q is pressed, loop is ended and camera is turned off
    if cv2.waitKey(1) == ord('q'):
        break


cam.release() #camera feed is released back to the system
cv2.destroyAllWindows() #All windows are closed




        
        
