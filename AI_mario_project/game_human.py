import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0,0,0)
YELLO = (255,255,0)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

BLOCK_SIZE = 20
SPEED = 20

PLAYER_SIZE = 20
food_SIZE = 20

PLAYER_SPEED = 5
JUMP_HEIGHT = 10

class MarioGame:
    
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Mario Game')
        self.clock = pygame.time.Clock()
        #self.image = pygame.Surface((20, 20))  # 創建一個矩形代表馬力歐的圖像
        #self.image.fill((0, 0, 255))
        #self.rect = self.image.get_rect()
        # init game state
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

    def _place_food(self):
        #x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        #y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        #self.food = Point(x, y)
        #if self.food in self.snake:
        #    self._place_food()
        self.food_x = random.randint(0, self.w - food_SIZE)
        self.food_y = self.h - food_SIZE
    def _place_trap(self):
        self.trap_x = random.randint(0, self.w - food_SIZE)
        self.trap_y = self.h - food_SIZE
        """
        if self.trap_x==(self.food_x or self.player_x) and self.trap_y==(self.food_y or self.player_y):
            self.trap_x = random.randint(0, self.w - food_SIZE)
            self.trap_y = self.h - food_SIZE
        """
        while(self.trap_x<(self.food_x+food_SIZE) and self.trap_x>(self.food_x-food_SIZE)):
            self.trap_x = random.randint(0, self.w - food_SIZE)
            self.trap_y = self.h - food_SIZE

    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.player_x>0:
                    self.direction = Direction.LEFT
                    self.player_x -= 20
                elif event.key == pygame.K_RIGHT and self.player_x<self.w-PLAYER_SIZE:
                    self.direction = Direction.RIGHT
                    self.player_x += 20
                elif event.key == pygame.K_UP and self.player_y>0:
                    self.direction = Direction.UP
                    self.jump_move = 1
                    #self.player_y -= 20
                elif event.key == pygame.K_DOWN and self.player_y<self.h-PLAYER_SIZE and self.jump_move!=1:
                    self.direction = Direction.DOWN
                    self.player_y += 20

        if self.jump_move == 1:
            self.player_y -= self.Y_VELOCITY
            self.Y_VELOCITY -= self.gravity
            if self.Y_VELOCITY < -self.JUMP_HEIGHT:
                self.jump_move = 0   
                self.Y_VELOCITY = self.JUMP_HEIGHT                
        # 2. move
        #self._gravity()
        #self._move(self.direction) # update the head
        #self.snake.insert(0, self.head)
        
        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move
        #if self.head == self.food:
            #self.score += 1
            #self._place_food()
        #else:
            #self.snake.pop()
        if self.player_x < self.food_x + food_SIZE and self.player_x + food_SIZE > self.food_x:
            if self.player_y < self.food_y + food_SIZE and self.player_y + food_SIZE > self.food_y:
                self.score += 1
                self._place_food()
                
        if(self.food_x > self.trap_x and self.trap_x > self.player_x):
            if(self.direction == Direction.RIGHT or self.direction==Direction.UP):
                reward = 10
        elif(self.food_x < self.trap_x and self.trap_x < self.player_x):
            if(self.direction == Direction.LEFT or self.direction==Direction.UP):
                reward = 10
            
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score
    
    def is_right(self,x,a): #(x,y)=>the middle,(a,b)=>the left or right one
        right=0
        if(a<=x/2):
            right=1
            return right
        else:
            right=0
            return right
    def is_left(self,x,a): #(x,y)=>the middle,(a,b)=>the left or right one
        left=0
        if(a>=x/2):
            left=1
            return left
        else:
            left=0
            return left    
    def is_up(self,x,a):
        up=0
        if(x<=a and a<=x+PLAYER_SIZE):
            up=1
            return up
        else:
            up=0
            return up
    def _is_collision(self):
        # hits boundary
        #if self.player_x > self.w - BLOCK_SIZE or self.player_y < 0:
        #    return True
        if self.player_x < self.trap_x + food_SIZE and self.player_x + food_SIZE > self.trap_x:
            if self.player_y < self.trap_y + food_SIZE and self.player_y + food_SIZE > self.trap_y:
                return True
        # hits itself
        #if self.head in self.snake[1:]:
        #    return True
        
        return False       
    
        
    def _update_ui(self):
        #self.display.fill(BLACK)
        background_image = pygame.image.load("img/background.png")  # 替换成您的背景图像文件的路径
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
        
        #self.player_rect = pygame.Rect(self.player_x, self.player_y, PLAYER_SIZE, PLAYER_SIZE)    
        #self.food_rect = pygame.Rect(self.food_x, self.food_y, food_SIZE, food_SIZE)
        #self.trap_rect = pygame.Rect(self.trap_x, self.trap_y, food_SIZE, food_SIZE)
        #pygame.draw.rect(self.display, WHITE, self.player_rect)
        #pygame.draw.rect(self.display, YELLO, self.food_rect)
        #pygame.draw.rect(self.display, RED, self.trap_rect)
       
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

 
    def _gravity(self):
        self.player_y += self.gravity
        print("FALLING")

    def _move(self, direction):
        x = self.player_x
        y = self.player_y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        print("MOVING")
        
            

if __name__ == '__main__':
    game = MarioGame()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            #break
            game._place_trap()
    print('Final Score', score)
        
        
    pygame.quit()