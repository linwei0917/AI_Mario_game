import torch
import random
import numpy as np
from collections import deque
from game import MarioGameAI, Direction
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0 
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # 如果資料超過popleft()
        self.model = Linear_QNet(13, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
        #head = game.snake[0]
        x=game.player_x
        y=game.player_y
        point_l = (x-20,y)
        point_r = (x+20,y)
        point_u = (x,y-20)
        #point_d = (x,y+20)
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        #dir_d = game.direction == Direction.DOWN
        state = [

            # Danger right
            (dir_r and game.is_collision(point_r)) or
            (dir_u and game.is_collision(point_r)),
            # Danger left 
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_l)),    
            # whether jumping
            game.jump_move,
            # Move direction
            dir_l,
            dir_r,
            dir_u,     
            # Food location 
            # food left
            game.food_x < game.player_x and game.food_x > game.trap_x,  
            game.food_x < game.player_x and game.food_x < game.trap_x and game.player_x<game.trap_x,
            game.food_x < game.player_x and game.food_x < game.trap_x and game.player_x>game.trap_x,
            # food right
            game.food_x > game.player_x and game.food_x < game.trap_x,
            game.food_x > game.player_x and game.food_x > game.trap_x and game.player_x<game.trap_x,
            game.food_x > game.player_x and game.food_x > game.trap_x and game.player_x>game.trap_x,
            #game.food_y < game.player_y,  # food up
            game.food_y > game.player_y  # food down
            ]

        return np.array(state, dtype=int)  #dype可以把True.Flase改成1或0

    #把資料存進矩陣內
    def remember(self, state, action, reward, next_state, done):
        #注意是雙括號
        self.memory.append((state, action, reward, next_state, done)) 

    #長期效益的訓練
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) 
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)
    
    #短期效益的訓練
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = MarioGameAI()
    while True:
        # 舊資料
        state_old = agent.get_state(game)

        # 取得行為
        final_move = agent.get_action(state_old)

        # 執行行為與得到新的狀態
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # 訓練短期記憶效益
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # 存取記憶
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # 劃出圖
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()