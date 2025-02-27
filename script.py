import pygame 
from sys import exit
import math
from settings import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Whispers of the Dead")
clock = pygame.time.Clock()

#load the images
background = pygame.transform.scale(pygame.image.load("background/0.jpeg").convert(), (WIDTH, HEIGHT))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load("player/0.png").convert_alpha(), 0, PLAYER_SIZE)
        self.bas_player_image = self.image
        self.hitbox_rect = self.bas_player_image.get_rect(center = self.pos) # used for detecting collisions
        self.rect = self.hitbox_rect.copy()
        self.speed = PLAYER_SPEED
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y) # used to offset the gun barrel from the player

    def player_rotation(self):
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = (self.mouse_coords[0] - self.hitbox_rect.centerx)
        self.y_change_mouse_player = (self.mouse_coords[1] - self.hitbox_rect.centery)
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.image = pygame.transform.rotate(self.bas_player_image, -self.angle - 90)
        self.rect = self.image.get_rect(center = self.hitbox_rect.center)
    
    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed

        # if player moves diagonally then reduce speed by divinding the speed by sqrt(2)
        if self.velocity_x !=0 and self.velocity_y != 0:
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        if pygame.mouse.get_pressed()== (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

    def is_shooting(self):
        if(self.shoot_cooldown == 0): # the user is only able to shoot if the cooldown = 0
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos = self.hitbox_rect.center + self.gun_barrel_offset.rotate(-self.angle) # the position of the bullet is the center of the player + the offset of the gun barrel
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)

    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()

        if(self.shoot_cooldown)> 0:
            self.shoot_cooldown -= 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("player/bullet.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, BULLET_SCALE)
        self.rect = self.image.get_rect(center = (x, y))
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.x_vel = math.cos(math.radians(self.angle))*self.speed
        self.y_vel = math.sin(math.radians(self.angle))*self.speed
        self.bullet_lifetime = BULLET_LIFETIME
        self.spawn_time= pygame.time.get_ticks() # used to determine when the bullet should be removed

    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.rect.x = self.x
        self.rect.y = self.y
        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime: # if the bullet has been alive for longer than the lifetime then remove it
            self.kill()

    def update(self):
        self.bullet_movement()
        

player = Player()

all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

all_sprites_group.add(player)

while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    screen.blit(background, (0, 0))

    all_sprites_group.draw(screen)
    bullet_group.draw(screen)
    all_sprites_group.update()
    bullet_group.update()


    pygame.display.update()
    clock.tick(FPS)