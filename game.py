#==========================================================================================================================================================================================

                                                                ###### IMPORTS ######
import pygame as pg
import os
import random
from threading import Timer

import cv2
import numpy as np

#==========================================================================================================================================================================================

                                                             ###### OBJECT TRACKING ######

class colorDetect():
    def __init__(self):
        self.x = 0
        self.y = 0

        #lower and upper bounds are set automatically to detect green
        self.lowerBound = np.array([33,80,40])
        self.upperBound = np.array([102,255,255])

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


        #Different frames are displayed
        cv2.imshow('camera', img) 
        
#==========================================================================================================================================================================================

                                                            ###### PYGAME CLASSES ######
#Initalizing game window and setting up dimensions
pg.init()

W, H = 1280, 720
win = pg.display.set_mode((W,H))

outsidev = 10


class wndControl():
    def __init__(self):
        self.startScreen = True
        self.detectScreen = False
        self.instScreen = False
        self.gameScreen = False
        self.timercalled = False
        self.shouldItime = True
        self.isPaused = False
        
        self.keyboard = False
        self.camera = False

        self.score = 0

        self.lives = 1
        
control = wndControl()


class fire():
    fire = pg.image.load(os.path.join('images','fire.png'))

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 89
        self.height = 119

    def draw(self, win):
        win.blit(self.fire, (self.x , self.y))
        pg.display.update()


#Coins 
class coins():
    #Pictures of coins are loaded
    coins = [pg.image.load(os.path.join('images','coin1.png')), pg.image.load(os.path.join('images','coin2.png')),
            pg.image.load(os.path.join('images','coin3.png')), pg.image.load(os.path.join('images','coin4.png')),
            pg.image.load(os.path.join('images','coin5.png'))]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        
        self.count = 0
        
    def draw(self, win):
        if self.count >= 10:
            self.count = 0
            
        #coin is animated
        win.blit(self.coins[self.count//2], (self.x, self.y))
        self.count += 1
        
        pg.display.update()



#Game Screen       
class Player():
    #Images are loaded
    backgrounds = [pg.image.load(os.path.join('images','game_bg_1.png')), pg.image.load(os.path.join('images','game_bg_2.png')),
          pg.image.load(os.path.join('images','game_bg_3.png')), pg.image.load(os.path.join('images','game_bg_4.png'))]

    bg = random.choice(backgrounds)

    back = pg.image.load(os.path.join('images','backbutton.png'))
    pause = pg.image.load(os.path.join('images','pausebutton.png'))
    resume = pg.image.load(os.path.join('images','resumebutton.png'))
    
    heart = pg.image.load(os.path.join('images','heart.png'))
    
    char = pg.image.load(os.path.join('images','Bstanding.png'))

    walkRight = [pg.image.load(os.path.join('images','BR1.png')), pg.image.load(os.path.join('images','BR2.png')),
                 pg.image.load(os.path.join('images','BR3.png'))]

    walkLeft = [pg.image.load(os.path.join('images','BL1.png')), pg.image.load(os.path.join('images','BL2.png')),
                 pg.image.load(os.path.join('images','BL3.png'))]

    font = pg.font.SysFont("comicsansms", 64)
    font2 = pg.font.SysFont("comicsansms", 160)
    font3 = pg.font.SysFont("comicsansms", 120)
    
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

    #function draws game screen
    def draw(self, win):
        heartsx = 90
        
        win.blit(self.bg, (self.bgx1, 0))
        win.blit(self.bg, (self.bgx2, 0))

        win.blit(self.back, (1150, 20))
        win.blit(self.pause, (550, 20))
        
        text = self.font.render("Score: " + str(control.score), True, (255,165,0))
        
        win.blit(text, (0,0))

        for i in range(control.lives):
            win.blit(self.heart, (heartsx*i, 80))
            
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

    #function that draws game over screen
    def draw2(self, win):
        text = self.font2.render("Game Over", True, (255,165,0))
        
        win.blit(text, (200,200))

        pg.display.update()

    #function that draws pause screen
    def draw3(self, win):
        text = self.font3.render("Game Paused", True, (255,165,0))

        win.blit(text, (200, 200))
        win.blit(self.resume, (500, 400))
        
        pg.display.update()
        

#Start screen
class startScreen():
    #Images are loaded
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


track = colorDetect()

#Instructions class
class cameraIns():
    bg = pg.image.load(os.path.join('images','instructions_screen.png'))
    
    def draw(self, win, keys):
        win.blit(self.bg, (0,0))
        
        #If a certain color is selected, lower and upper range for tracking is determined
        if keys[pg.K_g]:
            control.instScreen = not control.instScreen
            control.startScreen = not control.startScreen

        elif keys[pg.K_b]:
            control.instScreen = not control.instScreen
            control.startScreen = not control.startScreen
            
            track.lowerBound = np.array([110, 50, 50])
            track.upperBound = np.array([130,255,255])

        elif keys[pg.K_y]:
            control.instScreen = not control.instScreen
            control.startScreen = not control.startScreen
            
            track.lowerBound = np.array([20, 100, 100])
            track.upperBound = np.array([40,255,255])

        elif keys[pg.K_r]:
            control.instScreen = not control.instScreen
            control.startScreen = not control.startScreen
            
            track.lowerBound = np.array([30, 150, 50])
            track.upperBound = np.array([255,255,180])
            
        pg.display.update()

#==========================================================================================================================================================================================


clock = pg.time.Clock()
ply = Player(500,650,64,64)
start = startScreen()
inst = cameraIns()


#Game controls using tracking
def gamecntCamera(x, y):
    #If center of object touches back button then reset everything and go back to start screen 
    if 1155 <= x <= 1240 and 15 <= y <= 110:
        control.startScreen = True
        control.detectScreen = False
        control.instScreen = False
        control.gameScreen = False
        control.timercalled = False
        control.shouldItime = True
        
        control.keyboard = False
        control.camera = False

        control.score = 0

        control.lives = 1

    #If center of object touches pause button then pause game
    elif 550 <= mouse[0] <= 646 and 20 <= mouse[1] <= 110 and control.gameScreen and not control.isPaused:
        control.gameScreen = not control.gameScreen
        control.isPaused = not control.isPaused 
        ply.draw3(win)

    #If center of object touches resume button then resume game
    elif 500 <= mouse[0] <= 700 and 400 <= mouse[1] <= 600 and not control.gameScreen and control.isPaused:
        control.gameScreen = not control.gameScreen
        control.isPaused = not control.isPaused

    #Background keeps looping to give illusion character is always moving forward    
    if ply.bgx1 == ply.bg.get_width() * -1:
        ply.bgx1 = ply.bg.get_width()

    if ply.bgx2 == ply.bg.get_width() * -1:
        ply.bgx2 = ply.bg.get_width()
        

    #right
    if x <= 450:
        ply.left = False
        ply.right = True
        if ply.x >= W/2:
            ply.bgx1 -= 20
            ply.bgx2 -= 20

        else:
            ply.x += ply.velocity
            

    #left
    elif x >= 830 and ply.x >= (ply.velocity):
        ply.x -= ply.velocity
        ply.left = True
        ply.right = False
        
    #standing
    else:
        ply.left = False
        ply.right = False
        ply.runCount = 0

    #jump   
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


#Game controls using keyboard
def gamecntKeyboard(keys, mouse, clicked):

    #If back button is pressed then go back to start screen and reset variables
    if 1155 <= mouse[0] <= 1240 and 15 <= mouse[1] <= 110 and control.gameScreen:
        if clicked[0] == 1:
            control.startScreen = True
            control.detectScreen = False
            control.instScreen = False
            control.gameScreen = False
            control.timercalled = False
            control.shouldItime = True
            
            control.keyboard = False
            control.camera = False

            control.score = 0

            control.lives = 1

    #If pause button is pressed, then pause game
    elif 550 <= mouse[0] <= 646 and 20 <= mouse[1] <= 110 and control.gameScreen and not control.isPaused:
        if clicked[0] == 1:
            control.gameScreen = not control.gameScreen
            control.isPaused = not control.isPaused 
            ply.draw3(win)

    #If resume button is pressed then resume game
    elif 500 <= mouse[0] <= 700 and 400 <= mouse[1] <= 600 and not control.gameScreen and control.isPaused:
        if clicked[0] == 1:
            control.gameScreen = not control.gameScreen
            control.isPaused = not control.isPaused 

    #Background keeps looping around to give the illusion that character is moving forward
    if ply.bgx1 == ply.bg.get_width() * -1:
        ply.bgx1 = ply.bg.get_width()

    if ply.bgx2 == ply.bg.get_width() * -1:
        ply.bgx2 = ply.bg.get_width()
        
    #LEFT
    if keys[pg.K_LEFT] and ply.x >= (ply.velocity):
        ply.x -= ply.velocity
        ply.left = True
        ply.right = False

    #RIGHT
    elif keys[pg.K_RIGHT]:
        ply.left = False
        ply.right = True
        if ply.x >= W/2:
            ply.bgx1 -= 5
            ply.bgx2 -= 5

        else:
            ply.x += ply.velocity

    #STAND
    else:
        ply.left = False
        ply.right = False
        ply.runCount = 0

    #JUMP   
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




    
#==========================================================================================================================================================================================

objects1 = []
objects2 = []


coinstartingx = 500
firestartingx = 1500

def timerfun():
    global coinstartingx
    global firestartingx
    
    coinstartingx = coinstartingx + random.randrange(100, 600)
    objects1.append(coins(coinstartingx, 650))
    objects1.append(coins(coinstartingx+50, 650))
    objects1.append(coins(coinstartingx+100, 650))
    objects1.append(coins(coinstartingx+150, 650))
    objects1.append(coins(coinstartingx+200, 650))


    firestartingx += random.randrange(400, 700)
    objects2.append(fire(firestartingx, 620))

    t = Timer(6.0, timerfun)
    
    if control.shouldItime and control.gameScreen:
        t.start()

    
looprun = True
while looprun:
    mouse = pg.mouse.get_pos()
    clicked = pg.mouse.get_pressed()
    keys = pg.key.get_pressed()

    if control.timercalled == False and control.gameScreen:
        control.timercalled = True
        timerfun()
    
    if control.camera and control.detectScreen:
        track.detectfun()
        gamecntCamera(track.x, track.y)

    elif control.keyboard:
        gamecntKeyboard(keys, mouse, clicked)

    else:
        gamecntKeyboard(keys, mouse, clicked)


        
    if control.startScreen:
        start.draw(win, mouse, clicked) 

    elif control.instScreen:
        inst.draw(win, keys)


    elif control.gameScreen:
        ply.draw(win)
        
        for objectt1 in objects1:
            objectt1.draw(win)
            if ply.right:
                objectt1.x -= 5 

            if objectt1.x <= ply.x+ply.width/2 <= objectt1.x+objectt1.width and objectt1.y <= ply.y+ply.height/2 <= objectt1.y+objectt1.height:
                objects1.pop(objects1.index(objectt1))
                control.score += 10
                ply.draw(win)

        for objectt2 in objects2:
            objectt2.draw(win)
            if ply.right:
                objectt2.x -= 5 

            if objectt2.x <= ply.x+ply.width/2 <= objectt2.x+objectt2.width and objectt2.y <= ply.y+ply.height/2 <= objectt2.y+objectt2.height:
                objects2.pop(objects2.index(objectt2))
                control.lives -= 1
                ply.draw(win)

                if control.lives == 0:
                    control.gameScreen = not control.gameScreen
                    ply.draw2(win)
                    control.shouldItime = False
                    break


        
    for event in pg.event.get():
        if event.type == pg.QUIT:
            looprun = False

     
pg.quit()

track.cam.release() #camera feed is released back to the system
cv2.destroyAllWindows() #All windows are closed

