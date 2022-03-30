"""
Ryan Winnicki

Q-learning Agent created using Pytorch that plays a pong type game in pygame. 
This file contains the main function to run the program.

"""


import random
import numpy as np
import torch
from collections import deque
from pong import playGame
from helper import plot
from model import Linear_Qnet, QTrainer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MAX_MEMORY = 1000000
BATCH_SIZE = 1000
LR = .001

#agent
class Agent:
    def __init__(self):

        self.score = 0
        self.record = 0
        self.r_left = 0
        self.r_right = 0
        self.r_nothing = 0

        self.c_left = 0
        self.c_right = 0
        self.c_nothing = 0

        
        self.n_games = 0
        self.epsilon = 0 #randomness
        self.gamma = .9 #discount rate
        self.memory = deque(maxlen=MAX_MEMORY) #popleft if goes over memory
        self.model = Linear_Qnet(7, 64, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        self.model.cuda()
    
    def getRecord(self):
        return self.record

    def setRecord(self, record):
        self.record = record

    def getScore(self):
        return self.score
    
    def setScore(self,score):
        self.score = score

    def getGames(self):
        return self.n_games
    
    def addGame(self):
        self.n_games += 1

    def get_state(self, game):
        player = game.getPlayer()
        ball1 = game.getBall1()
        ball2 = game.getBall2()

        px, py, pw, ph = player.getPlayerInfo()
        b1x, b1y = ball1.getXY()
        b2x, b2y = ball2.getXY()

        state = [
        #player under ball1
        (px < b1x and b1x < (px+pw)),
        #player left of ball1
        ((px+pw) < b1x),
        #player right of ball1
        (px > b1x),
        #player under ball2
        (px < b2x and b2x < (px+pw)),
        #player left of ball2
        ((px+pw) < b2x),
        #player right of ball2
        (px > b2x),
        #ball1 closer to player than ball2
        (b1y < b2y)
        ]

        return np.array(state,dtype=int)

        

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 200 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
            if move == 0:
                self.r_left +=1
            elif move == 1:
                self.r_nothing +=1
            elif move == 2:
                self.r_right +=1
        else:
            state0 = torch.tensor(state, dtype=torch.float, device=device)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            if move == 0:
                self.c_left +=1
            elif move == 1:
                self.c_nothing +=1
            elif move == 2:
                self.c_right +=1

        return final_move

def train():
    totalReward = 0
    plot_scores = []
    plot_mean_scores = []
    total_score = 0

    agent = Agent()
    game = playGame()

    while True:
        #Get Old State
        state_old = agent.get_state(game)

        #Get Move
        final_move = agent.get_action(state_old)

        #preform move and get new State
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        #Set score to Agent
        agent.setScore(score)
        
        #train short term memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        
        #rememeber
        agent.remember(state_old, final_move, reward, state_new, done)
        #tracking total reward for session to see if we have improvement 
        totalReward += reward

        if done:
            agent.addGame()
            agent.train_long_memory()

            if agent.getScore() > agent.getRecord():
                agent.setRecord(score)
                agent.model.save()
            print("RL: ", agent.r_left, "RN: ", agent.r_nothing, "RR: ",agent.r_right)
            print("CL: ", agent.c_left, "CN: ", agent.c_nothing, "CR: ",agent.c_right)
            print("Game: ", agent.getGames(), 'Score: ', agent.getScore(), 'Record:', agent.getRecord(), "Reward: ", totalReward)
            agent.r_left = 0
            agent.r_nothing = 0
            agent.r_right = 0
            agent.c_left = 0
            agent.c_nothing = 0
            agent.c_right = 0
            totalReward = 0
            agent.setScore(0)
            game.reset()

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)



if __name__ == '__main__':
    train()