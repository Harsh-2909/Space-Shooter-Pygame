import pygame
import time
import os
import random

pygame.mixer.pre_init(44100, 16, 4, 4096) #frequency, size, channels, buffersize
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

# LOAD SOUND EFFECTS
explosion_sound = pygame.mixer.Sound(os.path.join("music", "explosion.wav"))
laser_sound = pygame.mixer.Sound(os.path.join("music", "laser.wav"))

# Laser Class for shooting lasers
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, laser_velo):
        self.y += laser_velo
    
    def off_screen(self, height):
        return self.y > height or self.y < 0
    
    def collision(self, obj):
        return collide(self, obj)

# Ship Parent class to inherit player and enemy ship class
class Ship:
    COOLDOWN = 30
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
        # DRAWING LASER
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                pygame.mixer.Channel(2).play(explosion_sound)
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            if sound_check(laser):
                pygame.mixer.Channel(0).play(laser_sound)
            self.lasers.append(laser)
            self.cool_down_counter = 1

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
    
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(-vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        pygame.mixer.Channel(2).play(explosion_sound)
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(WIN)


    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y+self.get_height()+10, self.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y+self.get_height()+10, int(self.get_width()*(self.health/self.max_health)), 10))

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

    def shoot(self): # To offset the laser position
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            if sound_check(laser):
                pygame.mixer.Channel(1).play(laser_sound)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def sound_check(obj: Laser): # To see if the laser is out of bound or not
    if obj.y < 0 or obj.y > 750:
        return False
    else:
        return True

def main():
    run = True
    lost = False
    lost_count = 0
    FPS = 60
    level = 0
    lives = 5
    PLAYER_VEL = 5
    ENEMY_VEL = 1
    LASER_VELO = 5
    enemies = []
    wave_length = 0
    main_font = pygame.font.SysFont("comicsans", size= 50)
    player = Player(300, 630)
    
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
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        
        # IF WE LOSE
        if lost:
            lost_label = main_font.render("YOU LOST!", 1, (255,255,255))
            WIN.blit(lost_label, ((WIDTH-lost_label.get_width())//2, (HEIGHT-lost_label.get_height())//2))
        
        # UPDATING THE DISPLAY
        pygame.display.update()
    
    while run:
        clock.tick(FPS)
        redraw_window() # UPDATING DISPLAY

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS*3:
                run = False
            else:
                continue
            
        # ADDING ENEMIES IN THE LIST AND SPAWNING THEM
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500 *(1+level//4), -100), random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - PLAYER_VEL > 0: # left
            player.x -= PLAYER_VEL
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + PLAYER_VEL + player.get_width() < WIDTH: # right
            player.x += PLAYER_VEL
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - PLAYER_VEL > 0: # up
            player.y -= PLAYER_VEL
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + PLAYER_VEL + player.get_height() + 15 < HEIGHT: # down
            player.y += PLAYER_VEL
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        mouse_press = pygame.mouse.get_pressed()
        if mouse_press[0]: # Fires the laser if the mouse key is pressed
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.move(ENEMY_VEL)
            enemy.move_lasers(LASER_VELO, player)
            if random.randrange(0, 2*FPS) == 1: # Or shoot every 2 second with randomness
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                pygame.mixer.Channel(2).play(explosion_sound)
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        player.move_lasers(LASER_VELO, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 75)
    run = True
    while run:
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(BG, (0,0))
        WIN.blit(title_label, ((WIDTH-title_label.get_width())//2, (HEIGHT-title_label.get_height())//2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()