import pygame as pg
import os
import random

import cv2
import numpy as np


class wndControl():
    def __init__(self):
        self.startScreen = True
        self.detectScreen = False
        self.instScreen = False
        self.gameScreen = False
        self.gameOver = False

        self.keyboard = False
        self.camera = False

        self.score = 0

control = wndControl()

class colorDetect():
    def __init__(self):
        self.x = 0
        self.y = 0
        
        self.lowerBound = np.array([33,80,40])
        self.upperBound = np.array([102,255,255])

##        self.lower_red = np.array([0,50,50]) #example value
##        self.upper_red = np.array([10,255,255]) #example value
        
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    def detectfun(self):
                
        #Current frame is read
        ret, img=self.cam.read()
        
        
        #Convert BGR to HSV
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


        #Create mask, which only has the color of the object that is being detected
        mask = cv2.inRange(imgHSV, self.lowerBound, self.upperBound)



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

            self.x = cX
            self.y = cY
##                if cX <= 250:
##                    print "right"
##
##                elif cX >= 391: 
##                    print "left"

                
        #Feature that allows user to select any object they want.
        #This will not analyze the color of the selected part as that causes a crash if it is kept in the code.


        #Pressing space will allow you to take a snapshot, then selecting a roi and pressing enter will display the roi.
        if cv2.waitKey(1) == 32:
            
            showCrosshair = False
            x0, y0, x1, y1 = cv2.selectROI("snapshot", img, showCrosshair)#selects roi(region of interest) and gives us the x and y coordinates of rectangle
            
            croppedImg = img[y0:y0+y1 , x0:x0+x1] #roi is selected from snapshot

    ##        #height and width are calculated
    ##        height = y1 
    ##        width = x1 

    ##        print "x0", x0
    ##        print "x1", x1
    ##        print "y0", y0
    ##        print "y1", y1

            b = 0
            g = 0
            r = 0

            count = 0
            
            for x in range(x1):
                for y in range(y1):
                    count += 1
                    colors = croppedImg[y, x]
                    b += colors[0]
                    g += colors[1]
                    r += colors[2]

    ##        color = np.uint8([[[b/count, g/count, r/count]]])
    ##        print color
    ##        pixel = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
    ##        print pixel
    ##        upper =  np.array([pixel[0] + 10, pixel[1] + 10, pixel[2] + 40])
    ##        lower =  np.array([pixel[0] - 10, pixel[1] - 10, pixel[2] - 40])
    ##
    ##        print pixel
    ##        print lower
    ##        print upper
    ##        
            cv2.imshow("croppedImg", croppedImg)


        #Different frames are displayed
        cv2.imshow('camera', img) #displays original frame with contours

        
        cv2.imshow('HSV', imgHSV) #displays hsv frame
##        cv2.imshow('mask&image Overlay', overlay) #displays mask 



##        #If q is pressed, loop is ended and camera is turned off
##        if cv2.waitKey(1) == ord('q'):
##            break
##
##
##
##
##




pg.init()

W, H = 1280, 720
win = pg.display.set_mode((W,H))

outsidev = 10


class coins():
    coins = [pg.image.load(os.path.join('images','coin1.png')), pg.image.load(os.path.join('images','coin2.png')),
            pg.image.load(os.path.join('images','coin3.png')), pg.image.load(os.path.join('images','coin4.png')),
            pg.image.load(os.path.join('images','coin5.png'))]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        
        self.count = 0
        
    def draw(self, win):
        if self.count >= 10:
            self.count = 0

        win.blit(self.coins[self.count//2], (self.x, self.y))
        self.count += 1
        
        pg.display.update()
        
class Player():
    backgrounds = [pg.image.load(os.path.join('images','game_bg_1.png')), pg.image.load(os.path.join('images','game_bg_2.png')),
          pg.image.load(os.path.join('images','game_bg_3.png')), pg.image.load(os.path.join('images','game_bg_4.png'))]

    bg = random.choice(backgrounds)
    
    char = pg.image.load(os.path.join('images','Bstanding.png'))

    walkRight = [pg.image.load(os.path.join('images','BR1.png')), pg.image.load(os.path.join('images','BR2.png')),
                 pg.image.load(os.path.join('images','BR3.png'))]

    walkLeft = [pg.image.load(os.path.join('images','BL1.png')), pg.image.load(os.path.join('images','BL2.png')),
                 pg.image.load(os.path.join('images','BL3.png'))]

    font = pg.font.SysFont("comicsansms", 64)
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.jumping = False
        self.jumpCount = 10
        self.runCount = 0
        self.right = False
        self.left = False
        self.velocity = 10

        self.bgx1 = 0
        self.bgx2 = self.bg.get_width()


    def draw(self, win):
        win.blit(self.bg, (self.bgx1, 0))
        win.blit(self.bg, (self.bgx2, 0))

        text = self.font.render("Score: " + str(control.score), True, (255,165,0))
        
        win.blit(text, (0,0))

        if self.runCount+1 > 9:
            self.runCount = 0
            
        if self.right:
            win.blit(self.walkRight[self.runCount//3], (self.x, self.y))
            self.runCount += 1

        elif self.left:
            win.blit(self.walkLeft[self.runCount//3], (self.x, self.y))
            self.runCount += 1

        else:
            win.blit(self.char, (self.x, self.y))


        pg.display.update()



class startScreen():
    bg = pg.image.load(os.path.join('images','skybg.png'))
    
    start = pg.image.load(os.path.join('images','start.png'))
    start_glow = pg.image.load(os.path.join('images','start_glow.png'))

    keyboard = [pg.image.load(os.path.join('images','keyboard.png')), pg.image.load(os.path.join('images','keyboard_selected.png'))]
    camera = [pg.image.load(os.path.join('images','camera.png')), pg.image.load(os.path.join('images','camera_selected.png'))]

    keyboard_check = False
    camera_check = False
    
     
    def draw(self, win, mouse, clicked):
        
        win.blit(self.bg, (0, 0))

        #START button
        if 515 <= mouse[0] <= 795 and 550 <= mouse[1] <= 629:
            win.blit(self.start_glow, (512, 550))

            if clicked[0] == 1:
                control.startScreen = not control.startScreen
                control.gameScreen = not control.gameScreen
                control.detectScreen = not control.detectScreen

        else:
            win.blit(self.start, (515, 550))


        #Keyboard icon
        if 850 <= mouse[0] <= 978 and 520 <= mouse[1] <= 648:
            if clicked[0] == 1 and not self.camera_check:
                self.keyboard_check = not self.keyboard_check
                control.keyboard = not control.keyboard



        #Camera icon
        if 280 <= mouse[0] <= 448 and 525 <= mouse[1] <= 648:
            if clicked[0] == 1 and not self.keyboard_check:
                control.camera = not control.camera
                control.startScreen = not control.startScreen
                control.instScreen = not control.instScreen
                self.camera_check = not self.camera_check
                
                
        if self.keyboard_check == False:       
            win.blit(self.keyboard[0], (850, 520))

        else:
            win.blit(self.keyboard[1], (850, 520))

        if self.camera_check == False:
            win.blit(self.camera[0], (280, 525))

        else:
            win.blit(self.camera[1], (280, 525))
        
        pg.display.update()


class cameraIns():
    bg = pg.image.load(os.path.join('images','instructions_screen.png'))
    
    def draw(self, win, keys):
        win.blit(self.bg, (0,0))

        if keys[pg.K_g]:
            control.instScreen = not control.instScreen
            control.startScreen = not control.startScreen
            

        pg.display.update()

clock = pg.time.Clock()
ply = Player(500,650,64,64)
track = colorDetect()
start = startScreen()
inst = cameraIns()




def gamecntCamera(x, y):
    
    if ply.bgx1 == ply.bg.get_width() * -1:
        ply.bgx1 = ply.bg.get_width()

    if ply.bgx2 == ply.bg.get_width() * -1:
        ply.bgx2 = ply.bg.get_width()
        

    #right
    if x <= 450:
        ply.left = False
        ply.right = True
        if ply.x >= W/2:
            ply.bgx1 -= 10
            ply.bgx2 -= 10

        else:
            ply.x += ply.velocity
            

    #left
    elif x >= 830 and ply.x >= (ply.velocity):
        ply.x -= ply.velocity
        ply.left = True
        ply.right = False
        

    else:
        ply.left = False
        ply.right = False
        ply.runCount = 0

        
    if not ply.jumping:
        if y <= 300:
            ply.jumping = True
            ply.left = False
            ply.right = False
            ply.runCount = 0

    else:
        if ply.jumpCount >= -10:
            neg = 1
            if ply.jumpCount < 0:
                neg = -1

            ply.y -= (ply.jumpCount ** 2) * 0.5 * neg
            ply.jumpCount -= 1

        else:
            ply.jumping = False
            ply.jumpCount = 10


def gamecntKeyboard(keys):
    
    if ply.bgx1 == ply.bg.get_width() * -1:
        ply.bgx1 = ply.bg.get_width()

    if ply.bgx2 == ply.bg.get_width() * -1:
        ply.bgx2 = ply.bg.get_width()
        
    
    if keys[pg.K_LEFT] and ply.x >= (ply.velocity):
        ply.x -= ply.velocity
        ply.left = True
        ply.right = False
        
    elif keys[pg.K_RIGHT]:
        ply.left = False
        ply.right = True
        if ply.x >= W/2:
            ply.bgx1 -= 5
            ply.bgx2 -= 5

        else:
            ply.x += ply.velocity

    else:
        ply.left = False
        ply.right = False
        ply.runCount = 0

        
    if not ply.jumping:
        if keys[pg.K_SPACE]:
            ply.jumping = True
            ply.left = False
            ply.right = False
            ply.runCount = 0

    else:
        if ply.jumpCount >= -10:
            neg = 1
            if ply.jumpCount < 0:
                neg = -1

            ply.y -= (ply.jumpCount ** 2) * 0.5 * neg
            ply.jumpCount -= 1

        else:
            ply.jumping = False
            ply.jumpCount = 10


MYEVENT = pg.USEREVENT + 1
time = [3000, 5000, 8000]
pg.time.set_timer(MYEVENT, random.choice(time))
objects = []

coinstartingx = 500

looprun = True
while looprun:
    mouse = pg.mouse.get_pos()
    clicked = pg.mouse.get_pressed()
    keys = pg.key.get_pressed()

    
    if control.camera and control.detectScreen:
        track.detectfun()
        gamecntCamera(track.x, track.y)

    elif control.keyboard:
        gamecntKeyboard(keys)
        
    if control.startScreen:
        start.draw(win, mouse, clicked) 

    elif control.instScreen:
        inst.draw(win, keys)

    elif control.gameScreen:
        ply.draw(win)
        
        for objectt in objects:
            objectt.draw(win)
            if ply.right:
                objectt.x -= 2

            if objectt.x <= ply.x+ply.width/2 <= objectt.x+objectt.width:
                objects.pop(objects.index(objectt))
                control.score += 10
                ply.draw(win)


    for event in pg.event.get():
        if event.type == pg.QUIT:
            looprun = False

        if event.type == MYEVENT:
            coinstartingx = coinstartingx + random.randrange(100, 600)
            objects.append(coins(coinstartingx, 650))
            objects.append(coins(coinstartingx+50, 650))
            objects.append(coins(coinstartingx+100, 650))
            objects.append(coins(coinstartingx+150, 650))
            objects.append(coins(coinstartingx+200, 650))

            
pg.quit()

track.cam.release() #camera feed is released back to the system
cv2.destroyAllWindows() #All windows are closed

