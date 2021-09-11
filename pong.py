from time import time, sleep
import pygame
import os
import time
import random



pygame.init()
pygame.font.init()

BLACK = (0,0,0)
WHITE = (255,255,255)
IDK = (100,100,100)

WIN_WIDTH = 600
WIN_HEIGHT = 800
LINE_WIDTH = 10
SPEED = 60
STAT_FONT = pygame.font.SysFont("comicsans", 50)
ND_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False
WIN = pygame.display.set_mode((WIN_WIDTH+LINE_WIDTH, WIN_HEIGHT+LINE_WIDTH))
pygame.display.set_caption("Pong")


class Window():


    def __init__(self, wn, player):
        self.background = pygame.Surface(wn.get_size())
        self.background = self.background.convert()
        self.background.fill(BLACK)
        
        # top line
        pygame.draw.rect(self.background, IDK, [0,0,WIN_WIDTH,LINE_WIDTH])
       
        # left line
        pygame.draw.rect(self.background, IDK, [0,0,LINE_WIDTH, WIN_HEIGHT])
        # right line
        pygame.draw.rect(self.background, IDK, [WIN_WIDTH,0,LINE_WIDTH, WIN_HEIGHT+LINE_WIDTH])
        
        self.score_label = STAT_FONT.render("Score: " + str(player.getScore()), 1 , (WHITE))
        wn.blit(self.score_label, (WIN_WIDTH - self.score_label.get_width() - 15, 10))
        wn.blit(self.background, (0, 0))

    def draw(self, wn, player):
        self.score_label = STAT_FONT.render("Score: " + str(player.getScore()), 1 , (WHITE))
        wn.blit(self.background, (0,0))
        wn.blit(self.score_label, (WIN_WIDTH - self.score_label.get_width() - 15, 10))

class Player:
    VEL =  30 % 780
    PAD_WIDTH = 90
    PAD_HEIGHT = 10
    REWARD = 0
    SCORE = 0

    def __init__(self, x, y):
        """
        Initialize the object
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
        if self.x > LINE_WIDTH:
            self.x -= self.VEL
        else:
            self.addReward(-1)
            self.x = LINE_WIDTH

    def moveRight(self):
        if self.x < WIN_WIDTH - LINE_WIDTH- self.PAD_WIDTH:
            self.x += self.VEL
        else:
            self.addReward(-1)
            self.x = WIN_WIDTH - LINE_WIDTH- self.PAD_WIDTH

    def getPlayerInfo(self):
        return self.x, self.y, self.PAD_WIDTH, self.PAD_HEIGHT

    def draw(self, wn):
        wn.blit(self.paddle, (self.x,self.y))
        #pygame.draw.rect(wn, WHITE, (self.x, self.y, self.PAD_WIDTH, self.PAD_HEIGHT))
    
    def getX(self):
        return self.x

class Ball:
    BALL_WIDTH = 20
    BALL_HEIGHT = 20
    RADIUS = 10
    DX = -2.3
    DY = 2

    def __init__(self, x, y, start):
        self.x = x
        self.y = y
        self.tickCount = 0
        self.v1 = pygame.math.Vector2(self.x, self.y)
        self.Dx = self.DX*start
        self.Dy = self.DY*start
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
        if(self.Dx < 8 or self.Dx > -8):
            r = random.uniform(1.0, 1.3)
            self.Dx *= r*x
        if(self.Dy < 8 or self.Dy > -8):
            r = random.uniform(1.0, 1.3)
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
                    self.Dx, self.Dy = m1.x*1.1, m1.y*1.1
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
                player.addReward(100)
            elif self.collide_floor():
                self.y = WIN_HEIGHT/2
                self.x = WIN_WIDTH/2
                self.Dy = self.DY*-1
                self.Dx = self.DX
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        if action == 0:
            self.player.addReward(-.1)
            self.player.moveLeft()
        if action == 2:
            self.player.addReward(-.1)
            self.player.moveRight()
                
        for ball in self.balls:
            check_game_over = ball.move(self.balls, self.player)
            if check_game_over:
                game_over = True
                self.player.addReward(-10)
                return self.player.getReward(), game_over, self.player.getScore()
                
        drawWindow(WIN, self.bg, self.player, self.balls)
        self.fps.tick(30)
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
