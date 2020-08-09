import pygame
import time
import os
import random

pygame.init()
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE SHOOTER")

# LOAD SPACESHIPS
RED_SPACESHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
BLUE_SPACESHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
GREEN_SPACESHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
YELLOW_SPACESHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# LOAD LASERS
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# LOAD BACKGROUND
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Ship Parent class to inherit player and enemy ship class
class Ship:
    def __init__(self, x, y, health= 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        # pygame.draw.rect(window, (255,0,0), (self.x, self.y, 50, 50), 0) # Window, Color, (Position, width, height), Thickness
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

# Player Ship class which inherits from Ship class
class Player(Ship):
    def __init__(self, x, y, health= 100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACESHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

# Enemy ship class which inherits from ship class
class Enemy(Ship):

    COLOR_MAP = {
        "red": (RED_SPACESHIP, RED_LASER),
        "blue": (BLUE_SPACESHIP, BLUE_LASER),
        "green": (GREEN_SPACESHIP, GREEN_LASER)
    }

    def __init__(self, x, y, color, health= 100):
        super().__init__(x, y, health)
        self.ship_img = self.COLOR_MAP[color][0]
        self.laser_img = self.COLOR_MAP[color][1]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def move(self, vel): # To move down the enemy ship
        self.y += vel

def main():
    run = True
    FPS = 60
    score = 0
    level = 1
    lives = 5
    PLAYER_VEL = 5
    main_font = pygame.font.SysFont("comicsans", size= 50)
    player = Player(300, 650)
    
    clock = pygame.time.Clock()

    def redraw_window():

        # DRAWING THE BACKGROUND
        WIN.blit(BG, (0,0))

        # DRAW TEXT
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # SHIP DRAWING
        player.draw(WIN)
        
        # UPDATING THE DISPLAY
        pygame.display.update()
    
    while run:
        clock.tick(FPS)
        redraw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - PLAYER_VEL > 0: # left
            player.x -= PLAYER_VEL
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + PLAYER_VEL + player.get_width() < WIDTH: # right
            player.x += PLAYER_VEL
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - PLAYER_VEL > 0: # up
            player.y -= PLAYER_VEL
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + PLAYER_VEL + player.get_height() < HEIGHT: # down
            player.y += PLAYER_VEL
main()