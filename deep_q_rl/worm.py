import numpy as np
import random
import pygame
from pygame.locals import *

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
NOTHING = 'rien'

WINDOWWIDTH = 84
WINDOWHEIGHT = 84
CELLSIZE = 3
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
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK


class Snake:

    action_list = (NOTHING,UP,DOWN,LEFT,RIGHT)
    nactions = len(action_list)

    def __init__(self, display=False):
        startx = random.randint(5, CELLWIDTH - 6)
        starty = random.randint(5, CELLHEIGHT - 6)
        self.wormCoords = [
            {'x': startx, 'y': starty},
            {'x': startx - 1, 'y': starty},
            {'x': startx - 2, 'y': starty}
        ]
        self.direction = RIGHT
        self.gameover = False
        self.apple = self.getRandomLocation()
        self.display = display

    def act(self, action):

        if self.action_list[int(action)] == LEFT and self.direction != RIGHT:
            self.direction = LEFT
        elif self.action_list[int(action)] == RIGHT and self.direction != LEFT:
            self.direction = RIGHT
        elif self.action_list[int(action)] == UP and self.direction != DOWN:
            self.direction = UP
        elif self.action_list[int(action)] == DOWN and self.direction != UP:
            self.direction = DOWN

        # check if the worm has hit itself or the edge
        if self.wormCoords[HEAD]['x'] == -1 or self.wormCoords[HEAD]['x'] == CELLWIDTH or self.wormCoords[HEAD]['y'] == -1 or self.wormCoords[HEAD]['y'] == CELLHEIGHT:
            self.gameover = True
            pygame.quit()
            self.reset_game()
            return -1 # game over
        for wormBody in self.wormCoords[1:]:
            if wormBody['x'] == self.wormCoords[HEAD]['x'] and wormBody['y'] == self.wormCoords[HEAD]['y']:
                self.gameover = True
                pygame.quit()
                self.reset_game()
                return -1 # game over

        reward = 0
        # check if worm has eaten an apply
        if self.wormCoords[HEAD]['x'] == self.apple['x'] and self.wormCoords[HEAD]['y'] == self.apple['y']:
            # don't remove worm's tail segment
            self.apple = self.getRandomLocation() # set a new apple somewhere
            reward = 1
        else:
            del self.wormCoords[-1] # remove worm's tail segment

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

        if self.wormCoords[HEAD]['x'] == -1 or self.wormCoords[HEAD]['x'] == CELLWIDTH or self.wormCoords[HEAD]['y'] == -1 or self.wormCoords[HEAD]['y'] == CELLHEIGHT:
            self.gameover = True
            pygame.quit()
            self.reset_game()
            return -1 # game over

        if self.display:
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(self.wormCoords)
            drawApple(self.apple)
            drawScore(len(self.wormCoords) - 3)
            pygame.display.update()
        return reward

    def getScreenGrayscale(self):
        array = np.zeros((WINDOWWIDTH,WINDOWHEIGHT))

        # snake
        for point in self.wormCoords:
            self._fillArray(array, point['x'], point['y'], CELLSIZE, 150)

        # apple
        self._fillArray(array, self.apple['x'], self.apple['y'], CELLSIZE, 255)
        return array

    def _fillArray(self,array,x,y,cellsize,color):
        for i in xrange(cellsize):
            for j in xrange(cellsize):
                try:
                    array[x*cellsize+j, y*cellsize+i] = color
                except:
                    import pdb; pdb.set_trace()

    def getMinimalActionSet(self):
        return np.asarray(range(5))

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
        self.direction = RIGHT
        self.gameover = False

        if self.display:
            global FPSCLOCK, DISPLAYSURF, BASICFONT

            pygame.init()
            DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
            BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
            pygame.display.set_caption('Wormy')

            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(self.wormCoords)
            drawApple(self.apple)
            drawScore(len(self.wormCoords) - 3)
            pygame.display.update()

    def getRandomLocation(self):
        return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)

def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))