"""
Ryan Winnicki
March 2022


This file contains all the classes to play a game simmilar to the classical game pong. This game is a single player game where 
the Player attempts to keep two balls "up", or from colliding with the ground. The player recieves a point for each successful paddle collision.

Game runs at maximum 100 frames per second.

Usually, there is a continual while loop to update the frame at each tick.
This is replaced by the play_step() function in the PlayGame() class so that information can be passed 
to the model before the next "step" or frame in the game.

Classes:
    Window() - draws the background, walls, and score of the game.
    Player() - The player is the paddle at the bottom of the screen. The class stores all information of the Player.
    Ball() - draws and contains all the information of the ball. There are two balls in this game.
    PlayGame() - contains all the functions to properly play the game at each step and reset the game if loss occurs.

"""



from time import time, sleep
import pygame
import os
import time
import random


pygame.init()
pygame.font.init()

# Setting colors that are used in drawing the game. 
BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (100,100,100)

#Setting the Window dimensions
WIN_WIDTH = 600
WIN_HEIGHT = 800

#Setting the Wall dimensions
LINE_WIDTH = 10

#Setting the font that will output the score.
STAT_FONT = pygame.font.SysFont("comicsans", 50)
ND_FONT = pygame.font.SysFont("comicsans", 70)

#Setting the Size of the Window and Caption
WIN = pygame.display.set_mode((WIN_WIDTH+LINE_WIDTH, WIN_HEIGHT+LINE_WIDTH))
pygame.display.set_caption("Pong")


class Window():
    """

    This is the drawing of the background, walls, and score text. The actual window is created when game is initiated.

    """
    
    def __init__(self, wn, player):
        """
        This initiates the draw of the background, wall, and score text.

            Args:
                wn - window that we are currently playing in.
                player - player information to get score.
        """
        self.background = pygame.Surface(wn.get_size())
        self.background = self.background.convert()
        self.background.fill(BLACK)
        
        # Top Wall
        pygame.draw.rect(self.background, GREY, [0,0,WIN_WIDTH,LINE_WIDTH])
       
        # Left Wall
        pygame.draw.rect(self.background, GREY, [0,0,LINE_WIDTH, WIN_HEIGHT+LINE_WIDTH])

        # Right Wall
        pygame.draw.rect(self.background, GREY, [WIN_WIDTH,0,LINE_WIDTH, WIN_HEIGHT+LINE_WIDTH])
        
        self.score_label = STAT_FONT.render("Score: " + str(player.getScore()), 1 , (WHITE))
        wn.blit(self.score_label, (WIN_WIDTH - self.score_label.get_width() - 15, 10))
        wn.blit(self.background, (0, 0))

    def draw(self, wn, player):
        """
        Updates the background and score text.

        --MUST UPDATE BACKGROUND-- 
        The player and balls will leave their remnants behind.

            Args:
                wn - window that we are currently playing in.
                player - player information to get score.
        """
        self.score_label = STAT_FONT.render("Score: " + str(player.getScore()), 1 , (WHITE))
        wn.blit(self.background, (0,0))
        wn.blit(self.score_label, (WIN_WIDTH - self.score_label.get_width() - 15, 10))





class Player:

    """
    Player is the paddle at the bottom of the game.

    Most functions are getters and setters besides movement and drawing. Collisions are tracked in the Ball Class.
    """

    #The speed at which the paddle will move. Trial and Error determined this was the best velocity so that the paddle smoothly stopped at boundries
    VEL =  30

    #Paddle dimensions
    PAD_WIDTH = 90
    PAD_HEIGHT = 10

    #Tracks Reward
    REWARD = 0

    #Tracks Score
    SCORE = 0

    def __init__(self, x, y):
        """
        Initialize the player object.

        x - x cordinates of player
        y - y cordinates of player

        """
        self.Score = self.SCORE
        self.x = x
        self.y = y
        self.reward = self.REWARD
        self.paddle = pygame.Surface((self.PAD_WIDTH, self.PAD_HEIGHT))
        self.paddle.fill(WHITE)

    def getY(self):
        return self.y

    def getHeight(self):
        return self.PAD_HEIGHT

    def resetReward(self):
        self.reward = 0

    def addReward(self, r):
        self.reward += r

    def getReward(self):
        return self.reward

    def getScore(self):
        return self.Score

    def addScore(self):
        self.Score += 1

    def resetScore(self):
        self.Score = 0

    def moveLeft(self):
        #self.addReward(-.1)
        if self.x > LINE_WIDTH:
            self.x -= self.VEL
        else:
            self.x = LINE_WIDTH

    def moveRight(self):
        #self.addReward(-.1)
        if self.x < WIN_WIDTH - LINE_WIDTH- self.PAD_WIDTH:
            self.x += self.VEL
        else:
            self.x = WIN_WIDTH - LINE_WIDTH- self.PAD_WIDTH

    def getPlayerInfo(self):
        return self.x, self.y, self.PAD_WIDTH, self.PAD_HEIGHT

    def draw(self, wn):
        wn.blit(self.paddle, (self.x,self.y))
        #pygame.draw.rect(wn, WHITE, (self.x, self.y, self.PAD_WIDTH, self.PAD_HEIGHT))
    
    def getX(self):
        return self.x

class Ball:
    """
    Balls are the objects the Player attempts to keep up.

    Movement and collisions with Player/Walls is tracked here. The balls speed up(increase velocity) as more collisions happen to increase difficulty.
    Max velocity of 4. Walls will increase velocity in the x direction and player/ceiling will increase velocity in y direction. Colliding with another 
    ball will increase velocity in both directions.
    """

    #Ball Dimensions
    BALL_WIDTH = 20
    BALL_HEIGHT = 20
    RADIUS = 10

    #Ball Velocity
    # DX (+) = moving right, (-) = moving left.
    # DY (+) = moving up, (-) = moving down.
    DX = -2.3
    DY = 2
    MAX_VELOCITY = 4


    def __init__(self, x, y, startDirection):
        """
        Initiates the x and y coordinates of the ball as well as the start direction.
        Creates a vector for later use when there is ball collisions.
        Will need to change wall and player collision later on to use vectors. May be more optimal.
        """
        self.x = x
        self.y = y
        self.tickCount = 0
        self.v1 = pygame.math.Vector2(self.x, self.y)
        self.Dx = self.DX*startDirection
        self.Dy = self.DY*startDirection
        self.ball = pygame.Surface((round(self.BALL_WIDTH), round(self.BALL_HEIGHT)))
        pygame.draw.circle(self.ball, pygame.Color("White"), (int(self.BALL_WIDTH/2),
                                                                 int(self.BALL_HEIGHT/2))
                                                                    , self.RADIUS)

    def getVector(self):
        return self.v1
    
    def getDxDy(self):
        return self.Dx, self.Dy
    
    def setDxDy(self, dx, dy):
        self.Dx = dx
        self.Dy = dy

    def getXY(self):
        return self.x, self.y

    def changeSpeed(self, x, y):
        if(self.Dx < self.MAX_VELOCITY or self.Dx > -self.MAX_VELOCITY):
            r = random.uniform(1.0, 1.1)
            self.Dx *= r*x
        if(self.Dy < self.MAX_VELOCITY or self.Dy > -self.MAX_VELOCITY):
            r = random.uniform(1.0, 1.1)
            self.Dy *= r*y

    def move(self, balls, player):
            for b in balls:
                bx, by = b.getDxDy()
                if b.getVector() == self.v1:
                    continue
                elif self.v1.distance_to(b.getVector()) < self.RADIUS*2 - 2:
                    nv = b.getVector()- self.v1
                    m1 = pygame.math.Vector2(self.Dx, self.Dy).reflect(nv)
                    m2 = pygame.math.Vector2(bx, by).reflect(nv)

                    #Sets new velocity of each ball
                    self.Dx, self.Dy = m1.x, m1.y
                    b.setDxDy(m2.x, m2.y)
                    
            if self.collide_wall():
                self.changeSpeed(-1, 1)
                self.x = self.x + self.Dx
            elif self.collide_ceiling():
                self.changeSpeed(1, -1)
                self.y = self.y + self.Dy
            elif self.collide_player(player):
                self.changeSpeed(1, -1)
                self.y = player.getY() - player.getHeight() - 3
                player.addScore()
                player.addReward(10)
            elif self.collide_floor():
                return True
            else:
                self.x = self.x + self.Dx
                self.y = self.y + self.Dy
            self.v1 = pygame.math.Vector2(self.x, self.y)
            return False
            
    def collide_wall(self):
        if self.x > 10 and self.x+self.BALL_WIDTH < WIN_WIDTH:
            return False
        return True

    def collide_ceiling(self):
        if self.y > LINE_WIDTH:
            return False
        return True

    def collide_player(self, player):
        px, py, pw, ph = player.getPlayerInfo()
        #if ball is inbetween player's y and y-height and ball is between player's x coordinates
        if (self.y > py-ph-2 and self.y < py) and (self.x < px+pw and self.x > px):
           return True
        return False

    def collide_floor(self):
        if self.y > WIN_HEIGHT-LINE_WIDTH:
            return True
        return False

    def draw(self, wn):
        wn.blit(self.ball, (self.x,self.y))



def drawWindow(wn, bg, player, balls):
    bg.draw(wn, player)
    player.draw(wn)
    for ball in balls:
        ball.draw(wn)

    pygame.display.update()
    

class playGame:

    def __init__(self):

        self.fps = pygame.time.Clock()
        self.player = Player(450,750)
        self.ball1 = Ball(WIN_WIDTH/3, 400, -1)
        self.ball2 = Ball(WIN_WIDTH*.66, 250, 1)

        self.balls = [self.ball1, self.ball2]
        self.bg = Window(WIN, self.player)

    def play_step(self, action):
        game_over = False
        self.player.resetReward()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        move = 0
        if action[0] == 1:
            move = 0
        elif action[1] == 1:
            move = 1
        elif action[2] == 1:
            move = 2
        if move == 0:
            self.player.moveLeft()
        if move == 2:
            self.player.moveRight()

        for ball in self.balls:
            check_game_over = ball.move(self.balls, self.player)
            if check_game_over:
                game_over = True
                self.player.addReward(-10)
                return self.player.getReward(), game_over, self.player.getScore()
                
        drawWindow(WIN, self.bg, self.player, self.balls)
        self.fps.tick(100)
        return self.player.getReward(), game_over, self.player.getScore()

           
    def reset(self):
        self.fps = pygame.time.Clock()
        self.player = Player(250,750)
        self.ball1 = Ball(WIN_WIDTH/3, 400, -1)
        self.ball2 = Ball(WIN_WIDTH*.66, 250, 1)

        self.balls = [self.ball1, self.ball2]
        self.bg = Window(WIN, self.player)

    def getPlayer(self):
        return self.player
    
    def getBall1(self):
        return self.ball1

    def getBall2(self):
        return self.ball2
