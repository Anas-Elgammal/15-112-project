#At the moment, this program only runs a really basic version of the game.

#This game is not connected with the tracking program and the object is moved through the arrow keys and space.


import pygame as pg

pg.init()

win = pg.display.set_mode((600,400)) #Puts window in fullscreen 
displayw, displayh = pg.display.get_surface().get_size() #gets height and width of screen
pg.display.set_caption("Game")



bg = pg.image.load('bg.png').convert()
bg.set_alpha(128)


#Characteristics of my character
cX = 0
cY = 330
cWidth = 50
cHeight = 60
cvel = 10

jumping = False
jumpCount = 10


looprun = True
while looprun:
    pg.time.delay(100) #delays reaction time by 100 milliseconds  

    for event in pg.event.get():
        if event.type == pg.QUIT:
            looprun = False

        if event.type is pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.display.set_mode((500, 500))

    keys = pg.key.get_pressed()


    if keys[pg.K_LEFT] and cX >= cvel:
        cX -= cvel
        
    if keys[pg.K_RIGHT] and cX <= displayw - (cWidth + cvel):
        cX += cvel

    if not jumping:

        if keys[pg.K_SPACE]:
            jumping = True

    else:
        if jumpCount >= -10:
            neg = 1
            if jumpCount < 0:
                neg = -1

            cY -= (jumpCount ** 2) * 0.5 * neg
            jumpCount -= 1

        else:
            jumping = False
            jumpCount = 10
            
    win.fill((0,0,0))
    win.blit(bg, (0,0))
    pg.draw.rect(win, (255, 0, 0), (cX, cY, cWidth, cHeight))
    pg.display.update()


pg.quit()
