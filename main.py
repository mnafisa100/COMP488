"""
Whispers of the Undead - Main Game Setup and Resource Initialization
This section includes screen setup, asset loading, game constants, 
initial story events, sound effects, and custom utility classes 
for core mechanics like blood essence and projectiles.
"""

import sys
import pygame
import math
import heapq
import random

pygame.init()

# ------------------------
# Screen and Clock Setup
# ------------------------
screen = pygame.display.set_mode((800, 700))
pygame.display.set_caption("Whispers of The Undead")
clock = pygame.time.Clock()

# ------------------------
# Background Setup
# ------------------------
# Scaled pixel-art background for the vampire castle scene
background = pygame.transform.scale(pygame.image.load("images/vampire_castle.png").convert(), (800, 700))

import textwrap  # Used for formatting long story text

# ------------------------
# Game Constants
# ------------------------
MAX_WAVES = 3             # Total number of waves before boss appears
FINAL_BOSS_WAVE = 3       # Wave at which the final boss is triggered

# ------------------------
# Load In-Game Assets
# ------------------------
partner_image = pygame.transform.scale(pygame.image.load("images/vampire_partner.png").convert_alpha(), (70, 70))
blood_essence_image = pygame.transform.scale(pygame.image.load("images/blood_essence.png").convert_alpha(), (30, 30))
vampire_lord_image = pygame.transform.scale(pygame.image.load("images/vampire_boss.png").convert_alpha(), (120, 120))
rescue_background = pygame.transform.scale(pygame.image.load("images/rescue_scene.png").convert(), (800, 700))

# ------------------------
# Story Events by Wave
# ------------------------
story_events = {
    1: "You awaken from centuries of slumber in this ancient castle. Your beloved partner is missing.",
    2: "Whispers in the shadows confirm your fears - the castle's master has taken your partner captive.",
    3: "The master's chamber lies ahead. You can sense your beloved's presence beyond.",
    "boss": "The ancient vampire lord stands between you and your partner. End this, once and for all."
}

# ------------------------
# Audio: Sound Effects & Music
# ------------------------
attack_sound = pygame.mixer.Sound("vampire_attack.mp3")
attack_sound.set_volume(0.2)

background_music = pygame.mixer.Sound("dark_ambience.mp3")
pygame.mixer.Channel(1).set_volume(0.5)

menu_sound = pygame.mixer.Sound("gothic_theme.mp3")
pygame.mixer.Channel(0).set_volume(0.5)
pygame.mixer.Channel(0).play(menu_sound, -1)

# ------------------------
# Room Layout Definition
# ------------------------
def create_room_layout():
    """
    Returns a dictionary defining rectangular boundaries of different rooms.
    Used for collision detection and rendering logic.
    """
    rooms = {
        "entrance": pygame.Rect(45, 110, 260, 440),
        "hallway": pygame.Rect(300, 200, 180, 80),
        "grand_hall": pygame.Rect(480, 110, 260, 440),
    }
    return rooms

# ------------------------
# Blood Essence System
# ------------------------
class BloodEssence:
    """
    Manages the player's blood essence resource used for healing or power-ups.
    Includes gain, use, display, and healing methods.
    """
    def __init__(self):
        self.current = 50
        self.maximum = 100
        self.font = pygame.font.Font(None, 30)
        self.image = blood_essence_image
    
    def update(self):
        """
        Placeholder for future blood essence behavior updates.
        """
        pass
    
    def gain(self, amount):
        """
        Increases blood essence by specified amount without exceeding maximum.
        """
        self.current = min(self.current + amount, self.maximum)
    
    def use(self, amount):
        """
        Uses specified amount of blood essence if available.
        Returns True if successful, else False.
        """
        if self.current >= amount:
            self.current -= amount
            return True
        return False
    
    def draw(self, screen):
        """
        Renders the blood essence UI bar and label on the screen.
        """
        font = pygame.font.Font(None, 36)
        
        essence_label = font.render("Blood Essence", True, (255, 215, 0))
        essence_shadow = font.render("Blood Essence", True, (0, 0, 0))
        
        label_x = screen.get_width() // 2 - essence_label.get_width() // 2
        image_x = label_x - self.image.get_width() - 5

        # Draw icon and label text
        screen.blit(essence_shadow, (label_x + 2, 17))  # Shadow drawn first
        screen.blit(essence_label, (label_x, 15))       # Then the label itself

        # Draw the essence container bar
        container_width = 150
        container_x = screen.get_width() // 2 - container_width // 2
        container_rect = pygame.Rect(container_x, 45, container_width, 15)
        pygame.draw.rect(screen, (50, 0, 0), container_rect)
        
        # Draw the filled portion based on current value
        if self.current > 0:
            blood_width = int(container_width * (self.current / self.maximum))
            blood_rect = pygame.Rect(container_x, 45, blood_width, 15)
            pygame.draw.rect(screen, (200, 0, 0), blood_rect)
    
    def heal_player(self):
        """
        Heals the player by 1 health if they are not at max health and have enough essence.
        Returns True if healing was successful.
        """
        if self.current >= 30 and player.health < player.max_health:
            self.current -= 30
            player.health += 1
            return True
        return False

# ------------------------
# Blood Projectile (Boss Attack)
# ------------------------
class BloodProjectile(pygame.sprite.Sprite):
    """
    Represents a blood orb projectile fired by the boss.
    Moves in a fixed direction and deals damage on contact.
    """
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 0, 0), (6, 6), 6)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 6
        self.lifetime = 120  # Frames before it disappears
        
    def update(self):
        """
        Moves the projectile and handles collisions and expiration.
        """
        # Move projectile
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

        # Deal damage to player on contact
        if self.rect.colliderect(player.hitbox_rect) and not player.invincible:
            player.health -= 1
            player.invincible = True
            player.invincibility_timer = 60  # Frames of invincibility
            self.kill()
        
        # Destroy projectile if it leaves bounds or hits invalid area
        if (self.rect.x < 0 or self.rect.x > 800 or 
            self.rect.y < 0 or self.rect.y > 700 or
            not is_within_playable_area(pygame.math.Vector2(self.rect.centerx, self.rect.centery))):
            self.kill()


# ------------------------
# BloodDrop Class
# ------------------------
class BloodDrop(pygame.sprite.Sprite):
    """
    Represents a blood essence collectible that drops from enemies or events.
    Adds to the player's blood essence when collected.
    """
    def __init__(self, x, y, amount):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (150, 0, 0), (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.amount = amount
        
    def update(self):
        # Check for collision with player and apply the essence bonus
        if pygame.sprite.collide_rect(self, player):
            player.blood_essence.gain(self.amount)
            self.kill()

# ------------------------
# Utility Functions for Room Boundaries
# ------------------------
def is_within_playable_area(position):
    """
    Checks if a given position (Vector2) is inside any defined playable room.
    Returns True if position is within a room.
    """
    rooms = create_room_layout()
    for room in rooms.values():
        if room.collidepoint(position):
            return True
    return False

def create_playable_area_grid(grid_size):
    """
    Creates a 2D grid representing walkable vs non-walkable areas.
    Used for movement and environmental restrictions.
    """
    grid = []
    for y in range(0, 700, grid_size):
        row = []
        for x in range(0, 800, grid_size):
            pos = pygame.math.Vector2(x, y)
            is_obstacle = not is_within_playable_area(pos)
            row.append(is_obstacle)
        grid.append(row)
    return grid

# ------------------------
# Start Menu Screen
# ------------------------
def start_menu():
    """
    Displays the start menu screen with title and start prompt.
    Waits for player to press SPACE to begin the game.
    """
    menu_font = pygame.font.Font(None, 48)
    title_font = pygame.font.Font(None, 72)
    
    title_text = title_font.render("Whispers of The Undead", True, (150, 0, 0))
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
    
    menu_text = menu_font.render("Press 'Space' to Start", True, (200, 200, 200))
    text_rect = menu_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    
    pygame.mixer.Channel(0).play(menu_sound, loops=-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Stop menu music and begin background music
                pygame.mixer.Channel(0).stop()
                pygame.mixer.Channel(1).play(background_music, loops=-1)
                return

        # Draw background with dark overlay
        screen.blit(background, (0, 0))
        overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Draw menu UI text
        screen.blit(title_text, title_rect)
        screen.blit(menu_text, text_rect)
        pygame.display.update()

# ------------------------
# Player Class
# ------------------------
class Player(pygame.sprite.Sprite):
    """
    Represents the main player character.
    Handles movement, attacking, health, room transitions, and special abilities.
    """
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(200, 500)
        self.image = pygame.transform.rotozoom(pygame.image.load('images/vampire_player.png').convert_alpha(), 0, 0.18)
        self.base_player_image = self.image

        # Collision hitbox
        self.hitbox_rect = self.base_player_image.get_rect(center=self.pos)
        self.hitbox_rect.height = 30
        self.rect = self.hitbox_rect.copy()

        # Combat and health
        self.can_attack = True
        self.attack_cooldown = 0
        self.health = 3
        self.max_health = 3
        self.invincible = False
        self.invincibility_timer = 0

        # Movement and environment
        self.grid_size = 15
        self.playable_area_grid = create_playable_area_grid(self.grid_size)
        self.current_room = "entrance"
        self.speed = 5

        # Power-up system
        self.blood_essence = BloodEssence()
        self.has_dash = False
        self.has_mist_form = False
        self.has_bat_transform = False

    def player_rotation(self):
        """
        Rotates player sprite to face the mouse pointer.
        """
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = self.mouse_coords[0] - self.hitbox_rect.centerx
        self.y_change_mouse_player = self.mouse_coords[1] - self.hitbox_rect.centery
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player)) + 90
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=self.hitbox_rect.center)

    def user_input(self):
        """
        Handles player input for movement, attacking, and abilities.
        """
        self.velocity_x = 0
        self.velocity_y = 0
        keys = pygame.key.get_pressed()

        # Movement inputs
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        
        # Normalize diagonal speed
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_y /= math.sqrt(2)
            self.velocity_x /= math.sqrt(2)

        # Mouse click attack
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            if self.can_attack:
                self.can_attack = False
                self.attack_cooldown = 20
                self.perform_attack()

        # Special abilities (if unlocked)
        if keys[pygame.K_q] and self.has_mist_form and self.blood_essence.use(20):
            self.activate_mist_form()
        if keys[pygame.K_e] and self.has_bat_transform and self.blood_essence.use(30):
            self.transform_to_bat()

    def perform_attack(self):
        """
        Fires a basic projectile in the direction the player is facing.
        """
        direction_vector = pygame.math.Vector2(math.cos(math.radians(self.angle - 90)), math.sin(math.radians(self.angle - 90)))
        attack_pos = self.pos + direction_vector * 40
        self.attack = VampireAttack(attack_pos.x, attack_pos.y, self.angle)
        attack_group.add(self.attack)
        all_sprites_group.add(self.attack)
        attack_sound.play()

    def dash(self):
        """
        Dashes the player in the current movement direction.
        """
        dash_distance = 3
        dash_vector = pygame.math.Vector2(self.velocity_x, self.velocity_y).normalize() * dash_distance * self.speed
        new_pos = self.pos + dash_vector
        if is_within_playable_area(new_pos):
            self.pos = new_pos

    def activate_mist_form(self):
        """
        Activates temporary invincibility using mist form.
        """
        self.invincible = True
        self.invincibility_timer = 120  # 2 seconds at 60 FPS

    def transform_to_bat(self):
        """
        Increases player speed temporarily when transformed into a bat.
        """
        self.speed = 10
        pygame.time.set_timer(pygame.USEREVENT, 3000)  # Reverts speed after 3 seconds

    def move(self):
        """
        Updates player position based on input and room boundaries.
        """
        new_pos = self.pos + pygame.math.Vector2(self.velocity_x, self.velocity_y)
        grid_x = int(new_pos.x / self.grid_size)
        grid_y = int(new_pos.y / self.grid_size)

        if 0 <= grid_x < len(self.playable_area_grid[0]) and 0 <= grid_y < len(self.playable_area_grid):
            if not self.playable_area_grid[grid_y][grid_x]:
                self.pos = new_pos

        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

        # Update current room based on new position
        rooms = create_room_layout()
        for room_name, room_rect in rooms.items():
            if room_rect.collidepoint(self.pos):
                self.current_room = room_name
                break

    def draw_health(self):
        """
        Draws player's heart-based health UI on screen.
        """
        heart_spacing = 30
        for i in range(self.max_health):
            heart_pos = (20 + i * heart_spacing, 20)
            if i < self.health:
                pygame.draw.circle(screen, (255, 0, 0), heart_pos, 10)
            else:
                pygame.draw.circle(screen, (255, 0, 0), heart_pos, 10, 2)

    def update(self):
        """
        Handles per-frame updates for input, health, blood essence, and room status.
        """
        self.user_input()
        self.move()
        self.player_rotation()
        self.blood_essence.update()

        # Handle attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0:
                self.can_attack = True

        # Handle temporary invincibility timer
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

        # UI rendering
        self.draw_health()
        self.blood_essence.draw(screen)

        # Display current room on screen
        font = pygame.font.Font(None, 36)
        room_text_str = f"Room: {self.current_room.replace('_', ' ').title()}"
        room_text = font.render(room_text_str, True, (255, 215, 0))
        room_shadow = font.render(room_text_str, True, (0, 0, 0))
        room_x = screen.get_width() - room_text.get_width() - 10
        screen.blit(room_shadow, (room_x + 2, 62))
        screen.blit(room_text, (room_x, 60))

# ------------------------
# VampireAttack Class
# ------------------------
class VampireAttack(pygame.sprite.Sprite):
    """
    Represents the player's melee or ranged attack (e.g., a slashing effect or projectile).
    Moves in the direction the player is facing and damages enemies on contact.
    """
    def __init__(self, x, y, attack_angle):
        super().__init__()
        self.original_image = pygame.transform.rotozoom(
            pygame.image.load('images/vampire_attack.png').convert_alpha(), 0, 1.2
        )
        self.attack_angle = attack_angle

        # Calculate direction vector from attack angle
        self.direction = pygame.math.Vector2(
            math.cos(math.radians(self.attack_angle - 90)), 
            math.sin(math.radians(self.attack_angle - 90))
        ).normalize()

        self.image = pygame.transform.rotate(self.original_image, -self.attack_angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(x, y)

        self.lifetime = 60           # Time in frames the attack lasts
        self.spawn_time = pygame.time.get_ticks()
        self.speed = 8               # Speed of the attack's movement

    def update(self):
        """
        Moves the attack forward, checks collision with enemies, and removes it after lifespan or off-screen.
        """
        self.position += self.direction * self.speed
        self.rect.center = (self.position.x, self.position.y)

        # Destroy if outside playable area
        if (self.position.x < 0 or self.position.x > 800 or 
            self.position.y < 0 or self.position.y > 700 or
            not is_within_playable_area(self.position)):
            self.kill()

        # Check collision with enemies
        enemy_hit = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in enemy_hit:
            if hasattr(enemy, 'take_damage'):
                enemy.take_damage(1)
                self.kill()
                break

# ------------------------
# BaseEnemy Class
# ------------------------
class BaseEnemy(pygame.sprite.Sprite):
    """
    Base class for all enemy types.
    Handles enemy AI states (hunt, dodge, recover), movement, health, pathfinding, and visual behavior.
    """
    def __init__(self, image_path, health=2, speed=2):
        super().__init__()
        original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.rotozoom(original_image, 0, 0.6)
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.hitbox_rect = self.base_image.get_rect(center=self.rect.center)

        self.grid_size = 15
        self.speed = speed
        self.path = []                       # Path to player
        self.path_update_timer = 100
        self.spawned = False
        self.rotation_angle = 0
        self.health = health
        self.state = "hunt"                  # Enemy AI state
        self.state_timer = 0
        self.blood_value = 10                # Amount of blood essence dropped on death

    def update_rotation(self, target_x, target_y):
        """
        Rotates enemy to face the player.
        """
        angle = math.degrees(math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx))
        self.rotation_angle = -angle - 90
        self.image = pygame.transform.rotate(self.base_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.hitbox_rect.center = self.rect.center

    def spawn_randomly(self, playable_area_grid, player_position, min_distance):
        """
        Spawns enemy at a random position within valid playable area 
        but at least a minimum distance from the player.
        """
        if not self.spawned:
            x, y = self.get_random_position(playable_area_grid, self.grid_size)
            distance_to_player = pygame.math.Vector2(x - player_position.x, y - player_position.y).length()
            if distance_to_player >= min_distance:
                self.rect.topleft = (x, y)
                self.spawned = True

    def get_random_position(self, playable_area_grid, grid_size):
        """
        Returns a random valid (non-obstacle) position from the grid.
        """
        valid_positions = []
        for y in range(0, len(playable_area_grid) * grid_size, grid_size):
            for x in range(0, len(playable_area_grid[0]) * grid_size, grid_size):
                grid_x = int(x / grid_size)
                grid_y = int(y / grid_size)
                if 0 <= grid_x < len(playable_area_grid[0]) and 0 <= grid_y < len(playable_area_grid):
                    if not playable_area_grid[grid_y][grid_x]:
                        valid_positions.append((x, y))
        return random.choice(valid_positions) if valid_positions else (0, 0)

    def get_grid_position(self):
        """
        Returns the enemy's current position in grid coordinates.
        """
        return int(self.rect.x / self.grid_size), int(self.rect.y / self.grid_size)

    def update_path_to_player(self, player_pos, playable_area_grid):
        """
        Updates the enemy's A* path to the player using heuristic search.
        """
        start = self.get_grid_position()
        goal = (int(player_pos.x / self.grid_size), int(player_pos.y / self.grid_size))
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        open_set = []
        heapq.heappush(open_set, (0, start))
        cost_to_point = {start: 0}
        came_from = {start: None}

        while open_set:
            current_cost, current_point = heapq.heappop(open_set)
            if current_point == goal:
                path = []
                while current_point:
                    path.append(current_point)
                    current_point = came_from[current_point]
                self.path = path[::-1]
                return

            for move in moves:
                new_point = (current_point[0] + move[0], current_point[1] + move[1])
                if (0 <= new_point[0] < len(playable_area_grid[0]) and
                    0 <= new_point[1] < len(playable_area_grid) and
                    not playable_area_grid[new_point[1]][new_point[0]]):
                    
                    new_cost = cost_to_point[current_point] + 1
                    if new_point not in cost_to_point or new_cost < cost_to_point[new_point]:
                        cost_to_point[new_point] = new_cost
                        priority = (new_cost + self.heuristic(new_point, goal), new_point)
                        heapq.heappush(open_set, priority)
                        came_from[new_point] = current_point
        self.path = []

    def heuristic(self, a, b):
        """
        Returns Euclidean distance heuristic between two grid points.
        """
        return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

    def move_towards_player_astar(self, playable_area_grid):
        """
        Moves enemy one step along the computed A* path towards the player.
        """
        if self.path:
            for next_point in reversed(self.path):
                target_x = next_point[0] * self.grid_size + self.grid_size / 2
                target_y = next_point[1] * self.grid_size + self.grid_size / 2
                direction = pygame.math.Vector2(target_x - self.rect.x, target_y - self.rect.y).normalize()
                new_rect = self.rect.move(direction.x * self.speed, direction.y * self.speed)

                grid_x = int(new_rect.x / self.grid_size)
                grid_y = int(new_rect.y / self.grid_size)

                if (0 <= grid_x < len(playable_area_grid[0]) and
                    0 <= grid_y < len(playable_area_grid) and
                    not playable_area_grid[grid_y][grid_x]):
                    self.rect = new_rect
                    break

    def draw_health_bar(self):
        """
        Draws a dynamic health bar above the enemy based on current health.
        """
        health_ratio = self.health / 2
        bar_width = 40
        bar_height = 5
        health_bar_width = int(bar_width * health_ratio)
        health_bar_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(health_bar_surface, (255, 255, 255), (0, 0, bar_width, bar_height))

        # Change color based on remaining health
        color = (0, 255, 0) if health_ratio > 0.6 else (255, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
        pygame.draw.rect(health_bar_surface, color, (0, 0, health_bar_width, bar_height))

        health_bar_pos = (self.rect.centerx - bar_width // 2, self.rect.y - 10)
        screen.blit(health_bar_surface, health_bar_pos)

    def take_damage(self, amount):
        """
        Reduces enemy health. On death, spawns a blood drop and removes the enemy.
        """
        self.health -= amount
        if self.health <= 0:
            blood_drop = BloodDrop(self.rect.centerx, self.rect.centery, self.blood_value)
            pickup_group.add(blood_drop)
            all_sprites_group.add(blood_drop)
            self.kill()
        else:
            self.state = "hunt"  # Optional: enforce aggressive behavior after taking damage

    def change_state(self, new_state):
        """
        Changes the AI state and resets the timer for the state duration.
        """
        self.state = new_state
        self.state_timer = random.randint(60, 120)

    def update(self):
        """
        Main per-frame update loop for AI logic and interactions.
        """
        if not self.spawned:
            self.spawn_randomly(player.playable_area_grid, player.pos, 150)
        else:
            if self.state == "hunt":
                if self.path_update_timer <= 0:
                    self.update_path_to_player(player.pos, player.playable_area_grid)
                    self.path_update_timer = 10
                else:
                    self.path_update_timer -= 1
                self.move_towards_player_astar(player.playable_area_grid)

            elif self.state == "dodge":
                # Move away from player
                direction = pygame.math.Vector2(self.rect.centerx - player.pos.x, self.rect.centery - player.pos.y).normalize()
                new_rect = self.rect.move(direction.x * self.speed * 1.5, direction.y * self.speed * 1.5)
                self.rect = new_rect

            elif self.state == "recover":
                pass  # Could add regeneration or delay behavior here

            # Timer-based state reset
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.change_state("hunt")

            # Face the player
            self.update_rotation(player.pos.x, player.pos.y)

            # Display health bar
            self.draw_health_bar()

            # Deal contact damage to player
            if self.rect.colliderect(player.hitbox_rect) and not player.invincible:
                player.health -= 1
                player.invincible = True
                player.invincibility_timer = 60  # 1 second at 60 FPS

# ------------------------
# VampireLord (Boss Enemy)
# ------------------------
class VampireLord(BaseEnemy):
    """
    Final boss enemy with multi-phase behaviors.
    Changes attack strategy and visual appearance based on remaining health.
    """
    def __init__(self):
        super().__init__("images/vampire_boss.png", health=6, speed=3)
        self.image = vampire_lord_image
        self.base_image = vampire_lord_image
        self.blood_value = 50
        self.phase = 1
        self.can_teleport = True
        self.teleport_cooldown = 0
        self.summon_cooldown = 0
        self.attack_cooldown = 0
        self.rect = self.image.get_rect()
        self.active_minions = 0
        self.max_minions = 3

    def update(self):
        """
        Controls boss behavior across three health-based phases.
        Each phase has unique patterns (summoning, charging, teleporting).
        """
        if not self.spawned:
            self.rect.center = (610, 330)
            self.spawned = True
        else:
            if self.health > 5:
                self.phase = 1
                self.phase_one_behavior()
            elif self.health > 2:
                if self.phase == 1:
                    show_story_text("The vampire lord transforms into a giant bat!", 2000)
                    self.base_image = pygame.transform.rotozoom(self.base_image, 0, 1.2)
                self.phase = 2
                self.phase_two_behavior()
            else:
                if self.phase == 2:
                    show_story_text("The vampire lord enters a blood rage!", 2000)
                    red_overlay = pygame.Surface(self.base_image.get_size(), pygame.SRCALPHA)
                    red_overlay.fill((255, 0, 0, 100))
                    self.base_image.blit(red_overlay, (0, 0))
                self.phase = 3
                self.phase_three_behavior()

            self.update_rotation(player.pos.x, player.pos.y)
            self.draw_health_bar()

            # Damage the player on contact
            if self.rect.colliderect(player.hitbox_rect) and not player.invincible:
                player.health -= 1
                player.invincible = True
                player.invincibility_timer = 60

    def phase_one_behavior(self):
        """
        Phase 1: Maintains distance from player and summons Bats if under minion cap.
        """
        distance_to_player = pygame.math.Vector2(self.rect.centerx - player.pos.x,
                                                 self.rect.centery - player.pos.y).length()

        if distance_to_player < 200:
            direction = pygame.math.Vector2(self.rect.centerx - player.pos.x,
                                            self.rect.centery - player.pos.y).normalize()
            new_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery) + direction * self.speed
            if is_within_playable_area(new_pos):
                self.rect.center = new_pos

        # Summon bats if allowed
        self.active_minions = len([e for e in enemy_group if isinstance(e, Ghoul)])
        if self.summon_cooldown <= 0 and self.active_minions < self.max_minions:
            ghoul = Ghoul()
            ghoul.rect.center = self.rect.center
            ghoul.spawned = True
            enemy_group.add(ghoul)
            all_sprites_group.add(ghoul)
            self.summon_cooldown = 180  # 3 seconds cooldown
        else:
            self.summon_cooldown -= 1

    def phase_two_behavior(self):
        """
        Phase 2: Increased speed, erratic movement, and aggressive dashes toward the player.
        """
        self.speed = 4

        # Random pathing around player
        if random.random() < 0.02:
            angle = random.randint(0, 360)
            direction = pygame.math.Vector2(math.cos(math.radians(angle)),
                                            math.sin(math.radians(angle))).normalize()
            target_pos = pygame.math.Vector2(player.pos.x, player.pos.y) + direction * 200
            if is_within_playable_area(target_pos):
                self.update_path_to_player(target_pos, player.playable_area_grid)

        if hasattr(self, 'path') and self.path:
            self.move_towards_player_astar(player.playable_area_grid)

        # Charge attack
        if self.attack_cooldown <= 0:
            self.speed = 8
            direction = pygame.math.Vector2(player.pos.x - self.rect.centerx,
                                            player.pos.y - self.rect.centery).normalize()
            new_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery) + direction * self.speed
            if is_within_playable_area(new_pos):
                self.rect.center = new_pos
            self.attack_cooldown = 120
        else:
            self.attack_cooldown -= 1
            if self.attack_cooldown == 60:
                self.speed = 4

    def phase_three_behavior(self):
        """
        Phase 3: Fast teleportation around player to confuse and overwhelm.
        """
        self.speed = 5

        if self.teleport_cooldown <= 0:
            angle = random.randint(0, 360)
            direction = pygame.math.Vector2(math.cos(math.radians(angle)),
                                            math.sin(math.radians(angle))).normalize()
            teleport_pos = pygame.math.Vector2(player.pos.x, player.pos.y) + direction * 100
            if is_within_playable_area(teleport_pos):
                self.rect.center = teleport_pos
            self.teleport_cooldown = 60  # 1 second cooldown
        else:
            self.teleport_cooldown -= 1

# ------------------------
# Bat (Minion Enemy)
# ------------------------
class Ghoul(BaseEnemy):
    """
    Small, fast enemy usually summoned by VampireLord.
    Appears smaller and weaker, but swarms the player.
    """
    def __init__(self):
        original_image_path = "images/ghoul.png"
        tiny_image = pygame.image.load(original_image_path).convert_alpha()
        tiny_image = pygame.transform.scale(tiny_image, (20, 20))

        super().__init__(original_image_path, health=2, speed=2)
        self.image = tiny_image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.blood_value = 10

# ------------------------
# Vampire (Teleporting Enemy)
# ------------------------
class Vampire(BaseEnemy):
    """
    Medium-health enemy that teleports behind the player if within range.
    Uses deceptive movement to evade direct attacks.
    """
    def __init__(self):
        super().__init__("images/vampire_enemy.png", health=3, speed=3)
        self.blood_value = 20
        self.can_teleport = True
        self.teleport_cooldown = 0

    def update(self):
        super().update()

        if self.can_teleport and self.teleport_cooldown <= 0:
            distance_to_player = pygame.math.Vector2(self.rect.centerx - player.pos.x,
                                                     self.rect.centery - player.pos.y).length()
            if 100 < distance_to_player < 200:
                behind_player = player.pos - pygame.math.Vector2(30, 0).rotate(player.angle)
                if is_within_playable_area(behind_player):
                    self.rect.center = behind_player
                    self.teleport_cooldown = 180  # 3 seconds cooldown

        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1

# ------------------------
# Werewolf (Rage Mechanic)
# ------------------------
class Werewolf(BaseEnemy):
    """
    Strong enemy that enrages and becomes faster when low on health.
    Visual transformation indicates state change.
    """
    def __init__(self):
        super().__init__("images/warewolf.png", health=4, speed=4)
        self.blood_value = 30
        self.enraged = False

    def update(self):
        super().update()

        # Rage state: Increase speed and scale up sprite
        if self.health <= 2 and not self.enraged:
            self.enraged = True
            self.speed = 6
            self.base_image = pygame.transform.rotozoom(self.base_image, 0, 1.2)
# ------------------------
# Boss Introduction Function
# ------------------------
def show_boss_intro():
    """
    Displays a flashing red screen sequence and introduces the final boss.
    """
    boss_intro_text = "The vampire lord appears! Defeat him to rescue your beloved!"
    
    # Flash red screen to signal boss appearance
    for _ in range(3):
        overlay = pygame.Surface((800, 700))
        overlay.fill((150, 0, 0))
        screen.blit(overlay, (0, 0))
        pygame.display.update()
        pygame.time.delay(100)

        # Re-draw background and sprites to clear flash
        screen.blit(background, (0, 0))
        all_sprites_group.draw(screen)
        pygame.display.update()
        pygame.time.delay(100)
    
    # Show the final story line before the battle
    show_story_text(story_events["boss"], 3000)

# ------------------------
# Enemy Spawning Logic
# ------------------------
def spawn_enemies(wave_number):
    """
    Spawns enemies based on the current wave number.
    Handles regular enemies for waves 1–3 and the Vampire Lord boss for wave 4.
    Returns a sprite group containing all spawned enemies.
    """
    enemies = pygame.sprite.Group()

    if wave_number <= MAX_WAVES:
        # Spawn bats
        num_ghouls = 3 if wave_number == 3 else wave_number * 2
        for i in range(num_ghouls):
            enemy = Ghoul()
            if wave_number == 3:
                enemy.health = 1
                enemy.speed = 1.5
                enemy.blood_value = 15
            enemy_group.add(enemy)
            all_sprites_group.add(enemy)
            enemies.add(enemy)

        # Spawn Vampires
        if wave_number >= 2:
            num_vampires = 1 if wave_number == 3 else wave_number - 1
            for i in range(num_vampires):
                enemy = Vampire()
                if wave_number == 3:
                    enemy.health = 2
                    enemy.speed = 2
                    enemy.teleport_cooldown = 300
                    enemy.blood_value = 30
                enemy_group.add(enemy)
                all_sprites_group.add(enemy)
                enemies.add(enemy)

        # Spawn a Werewolf only in final regular wave
        if wave_number == 3:
            enemy = Werewolf()
            enemy.health = 2
            enemy.speed = 3
            enemy.blood_value = 50
            enemy_group.add(enemy)
            all_sprites_group.add(enemy)
            enemies.add(enemy)

    elif wave_number == MAX_WAVES + 1:
        # Final boss spawn
        show_boss_intro()
        boss = VampireLord()
        enemy_group.add(boss)
        all_sprites_group.add(boss)
        enemies.add(boss)

    return enemies

# ------------------------
# Upgrade Selection Menu
# ------------------------
def show_upgrades():
    """
    Displays a choice of 1–3 random upgrades. Waits for player input to choose one.
    Applies the selected upgrade to the player.
    Returns the chosen upgrade effect as a string.
    """
    upgrades = [
        {"name": "Mist Form", "description": "Temporary invincibility", "effect": "mist"},
        {"name": "Bat Transform", "description": "Increased speed for a short time", "effect": "bat"},
        {"name": "Blood Capacity", "description": "Increase max blood essence", "effect": "blood"},
        {"name": "Health Up", "description": "Gain an extra heart", "effect": "health"}
    ]

    # Filter out already-unlocked upgrades
    available_upgrades = []
    for upgrade in upgrades:
        if upgrade["effect"] == "dash" and not player.has_dash:
            available_upgrades.append(upgrade)
        elif upgrade["effect"] == "mist" and not player.has_mist_form:
            available_upgrades.append(upgrade)
        elif upgrade["effect"] == "bat" and not player.has_bat_transform:
            available_upgrades.append(upgrade)
        elif upgrade["effect"] in ["blood", "health"]:
            available_upgrades.append(upgrade)

    # Pick 3 random upgrades
    chosen_upgrades = random.sample(available_upgrades, 3) if len(available_upgrades) > 3 else available_upgrades

    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    # Draw semi-transparent overlay
    overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    # Title
    title_text = font.render("Choose an Upgrade", True, (200, 0, 0))
    screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 100))

    # Draw upgrade cards
    for i, upgrade in enumerate(chosen_upgrades):
        x = 150 + i * 200
        pygame.draw.rect(screen, (50, 0, 0), (x, 200, 150, 200))
        pygame.draw.rect(screen, (100, 0, 0), (x, 200, 150, 200), 2)

        name_text = font.render(upgrade["name"], True, (200, 200, 200))
        screen.blit(name_text, (x + 75 - name_text.get_width() // 2, 220))

        desc_text = small_font.render(upgrade["description"], True, (200, 200, 200))
        screen.blit(desc_text, (x + 75 - desc_text.get_width() // 2, 280))

        key_text = font.render(f"Press {i+1}", True, (200, 200, 200))
        screen.blit(key_text, (x + 75 - key_text.get_width() // 2, 350))

    pygame.display.update()

    # Wait for player selection
    waiting = True
    selection = None
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and len(chosen_upgrades) >= 1:
                    selection = chosen_upgrades[0]["effect"]
                    waiting = False
                elif event.key == pygame.K_2 and len(chosen_upgrades) >= 2:
                    selection = chosen_upgrades[1]["effect"]
                    waiting = False
                elif event.key == pygame.K_3 and len(chosen_upgrades) >= 3:
                    selection = chosen_upgrades[2]["effect"]
                    waiting = False

    # Apply selected upgrade to player
    if selection == "dash":
        player.has_dash = True
    elif selection == "mist":
        player.has_mist_form = True
    elif selection == "bat":
        player.has_bat_transform = True
    elif selection == "blood":
        player.blood_essence.maximum += 25
        player.blood_essence.current += 25
    elif selection == "health":
        player.max_health += 1
        player.health += 1

    return selection
# ------------------------
# Victory Screen
# ------------------------
def victory_screen():
    """
    Displays the final victory screen after defeating the Vampire Lord.
    Shows the player reunited with their partner and offers a restart or quit.
    """
    screen.blit(rescue_background, (0, 0))

    # Semi-transparent overlay
    overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))

    font = pygame.font.Font(None, 72)
    victory_text = font.render('You Have Prevailed!', True, (200, 0, 0))
    text_rect = victory_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100))
    screen.blit(victory_text, text_rect)

    message_font = pygame.font.Font(None, 36)
    message_text = message_font.render('You have rescued your beloved from the vampire lord.', True, (200, 200, 200))
    message_rect = message_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(message_text, message_rect)

    # Player and partner sprites
    partner_rect = partner_image.get_rect(center=(screen.get_width() // 2 - 50, screen.get_height() // 2 + 100))
    player_rect = player.image.get_rect(center=(screen.get_width() // 2 + 50, screen.get_height() // 2 + 100))
    screen.blit(partner_image, partner_rect)
    screen.blit(player.image, player_rect)

    # Retry instructions
    retry_font = pygame.font.Font(None, 30)
    retry_text = retry_font.render('Press Space to Play Again or Escape to Quit', True, (200, 200, 200))
    retry_rect = retry_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 200))
    screen.blit(retry_text, retry_rect)

    pygame.display.update()

    # Music switch
    pygame.mixer.Channel(1).stop()
    pygame.mixer.Channel(0).play(menu_sound, loops=-1)

    waiting = True
    replay = False
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    replay = True
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    waiting = False

    pygame.mixer.Channel(0).stop()
    if replay:
        pygame.mixer.Channel(1).play(background_music, loops=-1)

    return replay

# ------------------------
# Game Over Screen
# ------------------------
def game_over_screen(wave_number):
    """
    Displays a game over screen when the player dies.
    Offers retry option to restart the game from wave 1.
    """
    screen.blit(background, (0, 0))
    overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    font = pygame.font.Font(None, 72)
    game_over_text = font.render('The Darkness Claims You', True, (150, 0, 0))

    # Shrink text if too wide
    if game_over_text.get_width() > screen.get_width() - 60:
        font = pygame.font.Font(None, 60)
        game_over_text = font.render('The Darkness Claims You', True, (150, 0, 0))

    text_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 80))
    screen.blit(game_over_text, text_rect)

    # Display wave reached
    wave_text = font.render(f'Wave: {current_wave}', True, (255, 215, 0))
    wave_text_shadow = font.render(f'Wave: {current_wave}', True, (0, 0, 0))
    screen.blit(wave_text_shadow, (12, 62))
    screen.blit(wave_text, (10, 60))

    # Retry instructions
    retry_font = pygame.font.Font(None, 30)
    retry_text = retry_font.render('Press Space to Retry', True, (200, 200, 200))
    retry_rect = retry_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 80))
    screen.blit(retry_text, retry_rect)

    pygame.display.update()
    pygame.mixer.Channel(1).stop()
    pygame.mixer.Channel(0).play(menu_sound, loops=-1)

    space_pressed = False
    while not space_pressed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                space_pressed = True

    # Clear enemies
    for enemy in enemy_group.sprites():
        enemy.kill()

    pygame.mixer.Channel(0).stop()
    pygame.mixer.Channel(1).play(background_music, loops=-1)
    return True

# ------------------------
# Story Text Display
# ------------------------
def show_story_text(text, duration=3000):
    """
    Displays a multi-line text overlay with styled background and border.
    Used for narrative moments.
    """
    font = pygame.font.Font(None, 36)
    words = text.split()
    lines, current_line = [], []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.render(test_line, True, (200, 200, 200)).get_width() > screen.get_width() - 100:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(' '.join(current_line))

    # Render text surfaces
    text_surfaces = [font.render(line, True, (255, 255, 255)) for line in lines]
    line_height = font.get_linesize()
    text_height = line_height * len(lines)
    max_width = max(surf.get_width() for surf in text_surfaces)

    # Create dark overlay with border
    overlay = pygame.Surface((max_width + 60, text_height + 60), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    pygame.draw.rect(overlay, (150, 0, 0), overlay.get_rect(), 2)

    overlay_y = screen.get_height() - text_height - 60

    # Show after a delay
    screen.blit(background, (0, 0))
    all_sprites_group.draw(screen)
    pygame.display.update()
    pygame.time.delay(1500)

    screen.blit(overlay, ((screen.get_width() - max_width - 60) // 2, overlay_y))
    for i, surf in enumerate(text_surfaces):
        text_rect = surf.get_rect(center=(screen.get_width() // 2, overlay_y + 30 + i * line_height))
        screen.blit(surf, text_rect)

    pygame.display.update()

    # Wait for duration or key press
    pygame.time.set_timer(pygame.USEREVENT + 1, duration)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.USEREVENT + 1):
                waiting = False

# ------------------------
# Area Transition Display
# ------------------------
def show_area_transition(area_name):
    """
    Displays a fade-in/fade-out text overlay indicating the new area entered.
    """
    font = pygame.font.Font(None, 48)
    text_surface = font.render(f"Entering: {area_name}", True, (150, 0, 0))
    if text_surface.get_width() > screen.get_width() - 60:
        font = pygame.font.Font(None, 36)
        text_surface = font.render(f"Entering: {area_name}", True, (150, 0, 0))

    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    for alpha in range(0, 255, 5):
        screen.blit(background, (0, 0))
        all_sprites_group.draw(screen)
        overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        alpha_surface = text_surface.copy()
        alpha_surface.set_alpha(alpha)
        screen.blit(alpha_surface, text_rect)
        pygame.display.update()
        pygame.time.delay(10)

    pygame.time.delay(1000)

    for alpha in range(255, 0, -5):
        screen.blit(background, (0, 0))
        all_sprites_group.draw(screen)
        overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        alpha_surface = text_surface.copy()
        alpha_surface.set_alpha(alpha)
        screen.blit(alpha_surface, text_rect)
        pygame.display.update()
        pygame.time.delay(10)

# ------------------------
# Main Game Loop
# ------------------------
# Sprite groups
all_sprites_group = pygame.sprite.Group()
attack_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
pickup_group = pygame.sprite.Group()

# Initialize player and first wave
player = Player()
all_sprites_group.add(player)
current_wave = 1
room_cleared = False
enemies = spawn_enemies(current_wave)
show_minimap = False

# Narrative and room tracking
story_events = {
    1: "You awaken from centuries of slumber in this ancient castle. Your beloved partner is missing.",
    2: "Whispers in the shadows confirm your fears - the castle's master has taken your partner captive.",
    3: "The master's chamber lies ahead. You can sense your beloved's presence beyond.",
    5: "Deep within these walls lies the ancient blood relic you seek.",
    7: "The castle's master approaches. Prepare yourself.",
    "boss": "The ancient vampire lord stands between you and your partner. End this, once and for all."
}
discovered_areas = set(["entrance"])
area_descriptions = {
    "entrance": "Castle Entrance - A foreboding gateway to darkness",
    "hallway": "Connecting Hallway - Shadows linger in every corner",
    "grand_hall": "Grand Hall - Once a place of nobility, now corrupted"
}

# Game state flags
running = True
show_menu = True
wave_transition_timer = 0
waiting_for_next_wave = False

# ------------------------
# Game Loop
# ------------------------
while running:
    if show_menu:
        start_menu()
        show_menu = False
        show_story_text(story_events[1])

    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            show_minimap = not show_minimap
        elif event.type == pygame.USEREVENT:
            player.speed = 5  # Reset bat speed

    # Wave indicator
    font = pygame.font.Font(None, 36)
    wave_text = font.render(f'Wave: {current_wave}', True, (255, 215, 0))
    wave_text_shadow = font.render(f'Wave: {current_wave}', True, (0, 0, 0))
    screen.blit(wave_text_shadow, (12, 62))
    screen.blit(wave_text, (10, 60))

    # Room discovery logic
    if player.current_room not in discovered_areas:
        discovered_areas.add(player.current_room)

    # Update attacks
    for attack in attack_group.sprites():
        attack.update()

    # Handle wave transitions and victory
    if len(enemy_group) == 0 and not room_cleared and not waiting_for_next_wave:
        if current_wave > MAX_WAVES:
            if victory_screen():
                # Reset state for replay
                player.health = player.max_health
                player.blood_essence.current = 50
                player.blood_essence.maximum = 100
                player.has_dash = player.has_mist_form = player.has_bat_transform = False
                current_wave = 1
                room_cleared = False
                enemies = spawn_enemies(current_wave)
                discovered_areas = set(["entrance"])
            else:
                running = False
        else:
            room_cleared = True
            waiting_for_next_wave = True
            wave_transition_timer = 60

    # Begin next wave after delay
    if waiting_for_next_wave:
        wave_transition_timer -= 1
        if wave_transition_timer <= 0:
            if current_wave in story_events:
                show_story_text(story_events[current_wave])

            if current_wave == MAX_WAVES:
                current_wave += 1
                enemies = spawn_enemies(current_wave)
            else:
                chosen_upgrade = show_upgrades()
                if chosen_upgrade:
                    show_story_text(f"New ability gained: {chosen_upgrade.replace('_', ' ').title()}")
                current_wave += 1
                enemies = spawn_enemies(current_wave)

            room_cleared = False
            waiting_for_next_wave = False

    # Show minimap if toggled
    if show_minimap:
        minimap_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        minimap_surface.fill((0, 0, 0, 150))
        rooms = create_room_layout()
        for room_name, room_rect in rooms.items():
            mini_rect = pygame.Rect(room_rect.x // 4 + 10, room_rect.y // 4 + 10, room_rect.width // 4, room_rect.height // 4)
            color = (100, 0, 0) if room_name in discovered_areas else (50, 50, 50)
            pygame.draw.rect(minimap_surface, color, mini_rect)
            if room_name == player.current_room:
                pygame.draw.rect(minimap_surface, (150, 0, 0), mini_rect, 2)

        # Player and enemy dots
        pygame.draw.circle(minimap_surface, (255, 255, 255), (player.pos.x // 4 + 10, player.pos.y // 4 + 10), 3)
        for enemy in enemy_group:
            pygame.draw.circle(minimap_surface, (255, 0, 0), (enemy.rect.centerx // 4 + 10, enemy.rect.centery // 4 + 10), 2)

        screen.blit(minimap_surface, (screen.get_width() - 210, screen.get_height() - 210))

    all_sprites_group.draw(screen)
    all_sprites_group.update()

    for pickup in pickup_group:
        pickup.update()

    # Handle player death
    if player.health <= 0:
        if game_over_screen(current_wave):
            # Reset game state on retry
            player.health = player.max_health
            player.blood_essence.current = 50
            player.blood_essence.maximum = 100
            player.has_dash = player.has_mist_form = player.has_bat_transform = False
            current_wave = 1
            room_cleared = False
            enemies = spawn_enemies(current_wave)
            discovered_areas = set(["entrance"])
        else:
            running = False

    pygame.display.update()
    clock.tick(60)
