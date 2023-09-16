import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

#colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0,0,0)
YELLO = (255,255,0)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3

#game_settings
BLOCK_SIZE = 20
SPEED = 400
PLAYER_SIZE = 20
food_SIZE = 20
PLAYER_SPEED = 5
JUMP_HEIGHT = 10

class MarioGameAI:
    
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Mario Game')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):    
        self.direction = Direction.RIGHT
        
        self.player_x = self.w//2
        self.player_y = self.h - PLAYER_SIZE
        
        self.jump_move = 0
        self.gravity = 2
        self.JUMP_HEIGHT = 20
        self.Y_VELOCITY = self.JUMP_HEIGHT

        self.score = 0
        self.food = None
        self._place_food()
        self._place_trap()
        self.frame_iteration = 0
        
    def _place_food(self):
        i=0
        if(i==0): #第一次
            self.food_x = random.randrange(food_SIZE, self.w - food_SIZE*2,food_SIZE) #min,max,step
            self.food_y = self.h - food_SIZE
            i+1
        else:
            self.food_x = random.randrange(food_SIZE, self.w - food_SIZE*2,food_SIZE) #min,max,step
            self.food_y = self.h - food_SIZE
            while(self.food_x<=(self.trap_x+food_SIZE*2) and self.food_x>=(self.trap_x-food_SIZE*2)):
                self.food_x = random.randrange(food_SIZE, self.w - food_SIZE*2,food_SIZE)
                self.food_x = self.h - food_SIZE

    def _place_trap(self):
        self.trap_x = random.randrange(food_SIZE*3, self.w - food_SIZE*3,food_SIZE)
        self.trap_y = self.h - food_SIZE
        while(self.trap_x<=(self.food_x+food_SIZE*2) and self.trap_x>=(self.food_x-food_SIZE*2)):
            self.trap_x = random.randrange(food_SIZE*3, self.w - food_SIZE*3,food_SIZE)
            self.trap_y = self.h - food_SIZE
       
    def play_step(self,action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move(jump,right,left)
        self._move(action) 
         
        # 3. check if game over
        reward = 0
        game_over = False
        
        # 4. "punish" for touching traps
        if self.is_collision() or self.frame_iteration > 100*(5): #自己定義
            game_over = True
            reward -= 10
            return reward,game_over, self.score
            
        # 5. "reward" for touching food,place new food or just move
        if self.player_x < self.food_x + food_SIZE and self.player_x + food_SIZE > self.food_x:
            if self.player_y < self.food_y + food_SIZE and self.player_y + food_SIZE > self.food_y:
                self.score += 1
                reward += 10
                self._place_food()

        # 6. "punish" for staying wall
        if self.player_x==0:
            reward -= 0.5
        if self.player_x==self.w-PLAYER_SIZE:
            reward -= 0.5
             
        
    def is_collision(self,pt=None):
        if pt is None:
            pt = (self.player_x,self.player_y)
        # touch traps
        if pt[0] < self.trap_x + food_SIZE and pt[0] + food_SIZE > self.trap_x:
            if pt[1] < self.trap_y + food_SIZE and pt[1] + food_SIZE > self.trap_y:
                return True     
        return False       
    
    def _update_ui(self):
        #self.display.fill(BLACK)
        background_image = pygame.image.load("img/background.png")
        background_image = pygame.transform.scale(background_image, (self.w, self.h))
        self.display.blit(background_image, (0, 0))
        player_image = pygame.image.load("img/player.png")
        coin_image = pygame.image.load("img/coin.png")
        trap_image = pygame.image.load("img/flower.png")
        if(self.direction==Direction.LEFT):
            player_image = pygame.transform.flip(player_image, True, False)
        player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
        self.display.blit(player_image, (self.player_x, self.player_y))
        coin_image = pygame.transform.scale(coin_image, (PLAYER_SIZE, PLAYER_SIZE))
        self.display.blit(coin_image, (self.food_x, self.food_y))
        trap_image = pygame.transform.scale(trap_image, (PLAYER_SIZE, PLAYER_SIZE))
        self.display.blit(trap_image, (self.trap_x, self.trap_y))
        """
        self.player_rect = pygame.Rect(self.player_x, self.player_y, PLAYER_SIZE, PLAYER_SIZE)
        self.food_rect = pygame.Rect(self.food_x, self.food_y, food_SIZE, food_SIZE)
        self.trap_rect = pygame.Rect(self.trap_x, self.trap_y, food_SIZE, food_SIZE)
        pygame.draw.rect(self.display, BLUE, self.player_rect)
        pygame.draw.rect(self.display, YELLO, self.food_rect)
        pygame.draw.rect(self.display, RED, self.trap_rect)
        """
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):

        if np.array_equal(action, [1, 0, 0]):   
            new_dir = Direction.UP # jump
        elif np.array_equal(action, [0, 1, 0]):
            new_dir = Direction.RIGHT # turn right
        else: # [0, 0, 1]
            new_dir = Direction.LEFT 
        self.direction = new_dir

        if self.direction == Direction.RIGHT and self.player_x>0:
            self.player_x -= 20
        elif self.direction == Direction.LEFT and self.player_x<self.w-PLAYER_SIZE:
            self.player_x += 20
        elif self.direction == Direction.UP and self.player_y>0:
            self.jump_move = 1
            #self.player_y -= 20
        #elif self.direction == Direction.DOWN and self.player_y<self.h-PLAYER_SIZE and self.jump_move!=1: 
        #    self.player_y += 20
        
        if self.jump_move == 1:
            self.player_y -= self.Y_VELOCITY
            self.Y_VELOCITY -= self.gravity
            if self.Y_VELOCITY < -self.JUMP_HEIGHT:
                self.jump_move = 0   
                self.Y_VELOCITY = self.JUMP_HEIGHT