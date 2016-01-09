import numpy as np
import random
import pygame
import time
from pygame.locals import *

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

WINDOWWIDTH = 84
WINDOWHEIGHT = 84
CELLSIZE = 6
ZOOM = 5
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

HEAD = 0
#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
EDGE      = (  0,  40,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

class Snake:

    action_list = (UP,DOWN,LEFT,RIGHT)
    nactions = len(action_list)

    def __init__(self, display=False, gameover=False):
        startx = random.randint(5, CELLWIDTH - 6)
        starty = random.randint(5, CELLHEIGHT - 6)
        self.wormCoords = [
            {'x': startx, 'y': starty},
            {'x': startx - 1, 'y': starty},
            {'x': startx - 2, 'y': starty}
        ]
        self.direction = DIRECTIONS[random.randint(0, 3)]
        self.gameover = gameover
        self.apple = self.getRandomLocation()
        self.display = display

    def act(self, action):

        if   action == 0:
            return 0
        elif action == LEFT and self.direction != RIGHT:
            self.direction = LEFT
        elif action == RIGHT and self.direction != LEFT:
            self.direction = RIGHT
        elif action == UP and self.direction != DOWN:
            self.direction = UP
        elif action == DOWN and self.direction != UP:
            self.direction = DOWN


        # move the worm by adding a segment in the direction it is moving
        if self.direction == UP:
            newHead = {'x': self.wormCoords[HEAD]['x'], 'y': self.wormCoords[HEAD]['y'] - 1}
        elif self.direction == DOWN:
            newHead = {'x': self.wormCoords[HEAD]['x'], 'y': self.wormCoords[HEAD]['y'] + 1}
        elif self.direction == LEFT:
            newHead = {'x': self.wormCoords[HEAD]['x'] - 1, 'y': self.wormCoords[HEAD]['y']}
        elif self.direction == RIGHT:
            newHead = {'x': self.wormCoords[HEAD]['x'] + 1, 'y': self.wormCoords[HEAD]['y']}

        self.wormCoords.insert(0, newHead)

        if self.wormCoords[HEAD]['x'] == 0 or self.wormCoords[HEAD]['x'] == CELLWIDTH - 1 or self.wormCoords[HEAD]['y'] == 0 or self.wormCoords[HEAD]['y'] == CELLHEIGHT - 1:
            self.gameover = True
            del self.wormCoords[0]
            #self.reset_game()
            return -1 # game over
        for wormBody in self.wormCoords[1:]:
            if wormBody['x'] == self.wormCoords[HEAD]['x'] and wormBody['y'] == self.wormCoords[HEAD]['y']:
                self.gameover = True
                del self.wormCoords[0]
                #self.reset_game()
                return -1 # game over

        reward = 0
        # check if worm has eaten an apple
        if self.wormCoords[HEAD]['x'] == self.apple['x'] and self.wormCoords[HEAD]['y'] == self.apple['y']:
            # don't remove worm's tail segment
            self.apple = self.getRandomLocation() # set a new apple somewhere
            reward = 1
        else:
            del self.wormCoords[-1] # remove worm's tail segment

        if self.display:
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(self.wormCoords)
            drawApple(self.apple)
            drawEdge()
            #drawScore(len(self.wormCoords) - 3)
            pygame.display.update()
        return reward

    def getScreenGrayscale(self):
        array = np.zeros((WINDOWWIDTH,WINDOWHEIGHT),dtype=np.uint8)

        # snake
        for point in self.wormCoords:
            self._fillArray(array, point['y'], point['x'], CELLSIZE, 100)
        self.__fillArray(array, self.wormCoords[HEAD]['y'], self.wormCoords[HEAD]['x'], CELLSIZE, 120)

        # apple
        self._fillArray(array, self.apple['y'], self.apple['x'], CELLSIZE, 255)

        # borders
        array[:CELLSIZE,:] = 100*np.ones((CELLSIZE,WINDOWHEIGHT))
        array[-CELLSIZE:,:] = 100*np.ones((CELLSIZE,WINDOWHEIGHT))
        array[:,:CELLSIZE] = 100*np.ones((WINDOWWIDTH,CELLSIZE))
        array[:,-CELLSIZE:] = 100*np.ones((WINDOWWIDTH,CELLSIZE))
        return array

    def _fillArray(self,array,x,y,cellsize,color):
        for i in xrange(cellsize):
            for j in xrange(cellsize):
                array[x*cellsize+j, y*cellsize+i] = color

    def getMinimalActionSet(self):
        return np.asarray(self.action_list)

    def getScreenDims(self):
        return WINDOWWIDTH, WINDOWHEIGHT

    def game_over(self):
        return self.gameover

    def reset_game(self):
        self.startx = random.randint(5, CELLWIDTH - 6)
        self.starty = random.randint(5, CELLHEIGHT - 6)
        self.wormCoords = [
            {'x': self.startx, 'y': self.starty},
            {'x': self.startx - 1, 'y': self.starty},
            {'x': self.startx - 2, 'y': self.starty}
        ]
        self.direction = DIRECTIONS[random.randint(0, 3)]
        self.gameover = False

        if self.display:
            global FPSCLOCK, DISPLAYSURF, BASICFONT

            pygame.init()
            DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH*ZOOM, WINDOWHEIGHT*ZOOM))
            BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
            pygame.display.set_caption('Wormy')

            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(self.wormCoords)
            drawApple(self.apple)
            drawEdge()
            #drawScore(len(self.wormCoords) - 3)
            pygame.display.update()

    def getRandomLocation(self, i=0):
        location = {'x': random.randint(1, CELLWIDTH - 2), 'y': random.randint(1, CELLHEIGHT - 2)}
        if location in self.wormCoords:
            return self.getRandomLocation(i+1)
        return location

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE * ZOOM
        y = coord['y'] * CELLSIZE * ZOOM
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE*ZOOM, CELLSIZE*ZOOM)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE*ZOOM - 8, CELLSIZE*ZOOM - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)

def drawApple(coord):
    x = coord['x'] * CELLSIZE * ZOOM
    y = coord['y'] * CELLSIZE * ZOOM
    appleRect = pygame.Rect(x, y, CELLSIZE*ZOOM, CELLSIZE*ZOOM)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH*ZOOM, CELLSIZE*ZOOM): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT*ZOOM))
    for y in range(0, WINDOWHEIGHT*ZOOM, CELLSIZE*ZOOM): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH*ZOOM, y))

def drawEdge():
    pygame.draw.rect(DISPLAYSURF, EDGE, (0, 0, WINDOWHEIGHT*ZOOM, CELLSIZE*ZOOM))
    pygame.draw.rect(DISPLAYSURF, EDGE, ((WINDOWHEIGHT - CELLSIZE)*ZOOM, 0, CELLSIZE*ZOOM, WINDOWHEIGHT*ZOOM ))
    pygame.draw.rect(DISPLAYSURF, EDGE, (0, 0, CELLSIZE*ZOOM, WINDOWWIDTH*ZOOM))
    pygame.draw.rect(DISPLAYSURF, EDGE, (0, (WINDOWWIDTH - CELLSIZE)*ZOOM, WINDOWWIDTH*ZOOM, CELLSIZE*ZOOM ))


