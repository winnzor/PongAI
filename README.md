# Pong Q-Learning Agent

This project creates an agent that teaches itself how to play a singleplayer version of the game pong. This version has two balls, instead
of one, where the object of the game is to keep the balls from hitting the ground.

You can find a video demo here.

## Game Enviornment

The game is created using the pygame library. The game starts with the player(paddle) on the bottom of the screen with two balls colliding in the middle of the screen. One ball will go toward the player while the other ball will go in the opposite direction to create a fair start. When the player succesfully keeps a ball from hitting the floor, the player will recieve one point. When the balls collide with different objects(Player/Walls/Other Balls), they speed up at a rate of 1.1x until they reach a maximum velocity to increase diffuclty as the game continues. When the player fails to keep up the ball, the player "loses" and the game will reset into the original starting posititon.

## Agent

Agent uses relu activation function with one hidden layer. The states of the game are fed into the model to determine if the player should move left, right, or no move. The model is rewarded +10 for every ball it succesfully keeps up, and -10 for every game over. The agent's moves are first randomized and gradually given control over it's own movements. By game 200, it has full control.

The states of the game:

    Player is left of ball1(True/False)
    Player is right of ball1(True/False)
    Player is under ball1(True/False)
    Player is left of ball2(True/False)
    Player is right of ball2(True/False)
    Player is under ball2(True/False)
    Ball1 is closer to player than ball2(True/False)

