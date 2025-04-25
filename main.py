import sys
import pygame
import math
import heapq
import random

pygame.init()



# Screen setup
screen = pygame.display.set_mode((800, 700))
pygame.display.set_caption("Whispers of The Undead")
clock = pygame.time.Clock()

# Load assets
background = pygame.transform.scale(pygame.image.load("images/vampire_castle.png").convert(), (800, 700))


import textwrap

# Game constants
MAX_WAVES = 3  # Game will end after this many waves
FINAL_BOSS_WAVE = 3  # When the vampire lord appears

# Add these at the beginning after other asset loading
partner_image = pygame.transform.scale(pygame.image.load("images/vampire_partner.png").convert_alpha(), (70, 70))
blood_essence_image = pygame.transform.scale(pygame.image.load("images/blood_essence.png").convert_alpha(), (30, 30))
vampire_lord_image = pygame.transform.scale(pygame.image.load("images/vampire_boss.png").convert_alpha(), (120, 120))
rescue_background = pygame.transform.scale(pygame.image.load("images/rescue_scene.png").convert(), (800, 700))

# Condensed story events for 3 waves plus boss
story_events = {
    1: "You awaken from centuries of slumber in this ancient castle. Your beloved partner is missing.",
    2: "Whispers in the shadows confirm your fears - the castle's master has taken your partner captive.",
    3: "The master's chamber lies ahead. You can sense your beloved's presence beyond.",
    "boss": "The ancient vampire lord stands between you and your partner. End this, once and for all."
}

# Sound effects
attack_sound = pygame.mixer.Sound("vampire_attack.mp3")
attack_sound.set_volume(0.2)

# Background music
background_music = pygame.mixer.Sound("dark_ambience.mp3")
pygame.mixer.Channel(1).set_volume(0.5)

# Menu music
menu_sound = pygame.mixer.Sound("gothic_theme.mp3")
pygame.mixer.Channel(0).set_volume(0.5)
pygame.mixer.Channel(0).play(menu_sound, -1)

# Game areas/rooms definitions
def create_room_layout():
    # Define different rooms in the castle
    rooms = {
        "entrance": pygame.Rect(45, 110, 260, 440),
        "hallway": pygame.Rect(300, 200, 180, 80),
        "grand_hall": pygame.Rect(480, 110, 260, 440),
        # Add more rooms as needed
    }
    return rooms

# Blood essence system
class BloodEssence:
    def __init__(self):
        self.current = 50
        self.maximum = 100
        self.font = pygame.font.Font(None, 30)
        self.image = blood_essence_image
    
    def update(self):
        # Blood essence no longer decreases over time
        pass
    
    def gain(self, amount):
        self.current = min(self.current + amount, self.maximum)
    
    def use(self, amount):
        if self.current >= amount:
            self.current -= amount
            return True
        return False
    
    def draw(self, screen):
        # Draw blood essence icon and text
        screen.blit(self.image, (screen.get_width() // 2 - 170, 40))
        
        text = self.font.render('Blood Essence:', True, (150, 0, 0))
        screen.blit(text, (screen.get_width() // 2 - 130, 45))
        
        # Draw the blood container
        container_rect = pygame.Rect(screen.get_width() // 2, 45, 100, 15)
        pygame.draw.rect(screen, (50, 0, 0), container_rect)
        
        # Draw the current blood level
        if self.current > 0:
            blood_rect = pygame.Rect(screen.get_width() // 2, 45, int(100 * (self.current / self.maximum)), 15)
            pygame.draw.rect(screen, (180, 0, 0), blood_rect)
            
    def heal_player(self):
        # New function to allow player to heal using blood essence
        if self.current >= 30 and player.health < player.max_health:
            self.current -= 30
            player.health += 1
            return True
        return False

# Add a Blood Projectile class for the boss
class BloodProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 0, 0), (6, 6), 6)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 6
        self.lifetime = 120  # 2 seconds at 60 FPS
        
    def update(self):
        # Move in the set direction
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        # Reduce lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            
        # Check for collisions with player
        if self.rect.colliderect(player.hitbox_rect) and not player.invincible:
            player.health -= 1
            player.invincible = True
            player.invincibility_timer = 60  # 1 second at 60 FPS
            self.kill()
            
        # Check if going out of bounds
        if (self.rect.x < 0 or self.rect.x > 800 or 
            self.rect.y < 0 or self.rect.y > 700 or
            not is_within_playable_area(pygame.math.Vector2(self.rect.centerx, self.rect.centery))):
            self.kill()



class BloodDrop(pygame.sprite.Sprite):
    def __init__(self, x, y, amount):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (150, 0, 0), (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.amount = amount
        
    def update(self):
        # Check if player collects this blood drop
        if pygame.sprite.collide_rect(self, player):
            player.blood_essence.gain(self.amount)
            self.kill()


def is_within_playable_area(position):
    rooms = create_room_layout()
    for room in rooms.values():
        if room.collidepoint(position):
            return True
    return False

def create_playable_area_grid(grid_size):
    grid = []
    for y in range(0, 700, grid_size):
        row = []
        for x in range(0, 800, grid_size):
            pos = pygame.math.Vector2(x, y)
            is_obstacle = not is_within_playable_area(pos)
            row.append(is_obstacle)
        grid.append(row)
    return grid

def start_menu():
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
                # Stop the start menu sound when the space key is pressed
                pygame.mixer.Channel(0).stop()
                pygame.mixer.Channel(1).play(background_music, loops=-1)
                return  # Exit the start menu if the space key is pressed

        screen.blit(background, (0, 0))
        # Add a semi-transparent overlay for better text visibility
        overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        screen.blit(title_text, title_rect)
        screen.blit(menu_text, text_rect)
        pygame.display.update()

# PLAYER
class Player(pygame.sprite.Sprite):
    # INITIAL CONSTRUCTOR
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(200, 500)
        self.image = pygame.transform.rotozoom(pygame.image.load('images/vampire_player.png').convert_alpha(), 0, 0.18)
        self.base_player_image = self.image
        # TO CHECK HITBOX
        self.hitbox_rect = self.base_player_image.get_rect(center=self.pos)
        self.hitbox_rect.height = 30
        # TO DRAW PLAYER ON SCREEN
        self.rect = self.hitbox_rect.copy()
        # attack properties
        self.can_attack = True
        self.attack_cooldown = 0
        self.health = 3  # Heart-based health system
        self.max_health = 3
        self.invincible = False
        self.invincibility_timer = 0
        self.grid_size = 15
        self.playable_area_grid = create_playable_area_grid(self.grid_size)
        # Vampire abilities
        self.blood_essence = BloodEssence()
        self.has_dash = False
        self.has_mist_form = False
        self.has_bat_transform = False
        self.current_room = "entrance"
        self.speed = 5

    # ROTATION
    def player_rotation(self):
        # GET MOUSE COORDINATES
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = (self.mouse_coords[0] - self.hitbox_rect.centerx)
        self.y_change_mouse_player = (self.mouse_coords[1] - self.hitbox_rect.centery)
        # ADDED 90 TO FIX CALCULATION FOR THE TIME BEING
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player)) + 90
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=self.hitbox_rect.center)

    # HANDLE USER INPUTS
    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            
        # MOVE DIAGONALLY / PYTHAGOREAN THEORY
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_y /= math.sqrt(2)
            self.velocity_x /= math.sqrt(2)
            
        # Attack - Only process mouse clicks for attacking, not for level progression
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left mouse button
            if self.can_attack:  # Remove blood essence requirement
                self.can_attack = False
                self.attack_cooldown = 20
                self.perform_attack()
                            
        if keys[pygame.K_q] and self.has_mist_form and self.blood_essence.use(20):
            self.activate_mist_form()
            
        if keys[pygame.K_e] and self.has_bat_transform and self.blood_essence.use(30):
            self.transform_to_bat()

    def perform_attack(self):
        # Calculate position slightly in front of the player based on the player's facing direction
        direction_vector = pygame.math.Vector2(math.cos(math.radians(self.angle - 90)), math.sin(math.radians(self.angle - 90)))
        attack_pos = self.pos + direction_vector * 40  # 40 pixels in front of player
        
        self.attack = VampireAttack(attack_pos.x, attack_pos.y, self.angle)
        attack_group.add(self.attack)
        all_sprites_group.add(self.attack)
        # Play the attack sound
        attack_sound.play()

    def dash(self):
        # Quick dash in the direction of movement
        dash_distance = 3
        dash_vector = pygame.math.Vector2(self.velocity_x, self.velocity_y).normalize() * dash_distance * self.speed
        new_pos = self.pos + dash_vector
        
        if is_within_playable_area(new_pos):
            self.pos = new_pos
            
    def activate_mist_form(self):
        # Temporary invincibility and ability to pass through enemies
        self.invincible = True
        self.invincibility_timer = 120  # 2 seconds at 60 FPS
        
    def transform_to_bat(self):
        # Temporary speed boost and ability to reach higher places
        self.speed = 10
        pygame.time.set_timer(pygame.USEREVENT, 3000)  # Revert after 3 seconds

    # CHANGE POSITION
    def move(self):
        new_pos = self.pos + pygame.math.Vector2(self.velocity_x, self.velocity_y)
        grid_x = int(new_pos.x / self.grid_size)
        grid_y = int(new_pos.y / self.grid_size)

        # Check if the new position is within the playable area grid
        if 0 <= grid_x < len(self.playable_area_grid[0]) and 0 <= grid_y < len(self.playable_area_grid):
            # Check if the new position is not an obstacle in the grid
            if not self.playable_area_grid[grid_y][grid_x]:
                self.pos = new_pos

        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center
        
        # Check which room player is in
        rooms = create_room_layout()
        for room_name, room_rect in rooms.items():
            if room_rect.collidepoint(self.pos):
                self.current_room = room_name
                break

    # DRAW HEALTH (HEARTS)
    def draw_health(self):
        heart_spacing = 30
        for i in range(self.max_health):
            heart_pos = (20 + i * heart_spacing, 20)
            if i < self.health:
                # Full heart
                pygame.draw.circle(screen, (255, 0, 0), heart_pos, 10)
            else:
                # Empty heart outline
                pygame.draw.circle(screen, (255, 0, 0), heart_pos, 10, 2)

    # UPDATE PLAYER STATE
    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()
        self.blood_essence.update()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0:
                self.can_attack = True
                
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False
                
        # Draw health and blood essence
        self.draw_health()
        self.blood_essence.draw(screen)
        
        # Display current room name
        font = pygame.font.Font(None, 24)
        room_text = font.render(f"Room: {self.current_room.replace('_', ' ').title()}", True, (200, 200, 200))
        screen.blit(room_text, (screen.get_width() - 200, 20))


class VampireAttack(pygame.sprite.Sprite):
    def __init__(self, x, y, attack_angle):
        super().__init__()
        self.original_image = pygame.transform.rotozoom(pygame.image.load('images/vampire_attack.png').convert_alpha(), 0, 1.2)
        self.attack_angle = attack_angle
        
        # Calculate the direction vector from angle
        self.direction = pygame.math.Vector2(
            math.cos(math.radians(self.attack_angle - 90)), 
            math.sin(math.radians(self.attack_angle - 90))
        ).normalize()
        
        # Rotate the image right away
        self.image = pygame.transform.rotate(self.original_image, -self.attack_angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(x, y)
        self.lifetime = 60  # Extended lifetime for projectile
        self.spawn_time = pygame.time.get_ticks()
        self.speed = 8  # Speed of the projectile
        
    def update(self):
        # Move the projectile in the direction
        self.position += self.direction * self.speed
        self.rect.center = (self.position.x, self.position.y)
        
        # Check if projectile hits a wall (goes out of screen or into non-playable area)
        if (self.position.x < 0 or self.position.x > 800 or 
            self.position.y < 0 or self.position.y > 700 or
            not is_within_playable_area(self.position)):
            self.kill()
            
        # Check for collisions with enemies
        enemy_hit = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in enemy_hit:
            # Only call take_damage on objects that have this method
            if hasattr(enemy, 'take_damage'):
                # Decrease enemy health
                enemy.take_damage(1)
                # Kill the projectile after hitting an enemy
                self.kill()
                break


class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, image_path, health=2, speed=2):
        super().__init__()
        original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.rotozoom(original_image, 0, 0.6)
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.hitbox_rect = self.base_image.get_rect(center=self.rect.center)
        self.grid_size = 15
        self.speed = speed
        self.path = []
        self.path_update_timer = 100
        self.spawned = False
        self.rotation_angle = 0
        self.health = health
        self.state = "hunt"  # Default state
        self.state_timer = 0
        self.blood_value = 10  # How much blood essence player gets from defeating this enemy
        
    def update_rotation(self, target_x, target_y):
        angle = math.degrees(math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx))
        self.rotation_angle = -angle - 90
        self.image = pygame.transform.rotate(self.base_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.hitbox_rect.center = self.rect.center

    def spawn_randomly(self, playable_area_grid, player_position, min_distance):
        if not self.spawned:
            x, y = self.get_random_position(playable_area_grid, self.grid_size)
            distance_to_player = pygame.math.Vector2(x - player_position.x, y - player_position.y).length()

            if distance_to_player >= min_distance:
                self.rect.topleft = (x, y)
                self.spawned = True

    def get_random_position(self, playable_area_grid, grid_size):
        valid_positions = []

        for y in range(0, len(playable_area_grid) * grid_size, grid_size):
            for x in range(0, len(playable_area_grid[0]) * grid_size, grid_size):
                grid_x = int(x / grid_size)
                grid_y = int(y / grid_size)

                if 0 <= grid_x < len(playable_area_grid[0]) and 0 <= grid_y < len(playable_area_grid):
                    if not playable_area_grid[grid_y][grid_x]:
                        valid_positions.append((x, y))

        if valid_positions:
            return random.choice(valid_positions)
        else:
            return 0, 0

    def get_grid_position(self):
        return int(self.rect.x / self.grid_size), int(self.rect.y / self.grid_size)

    # A* pathfinding algorithm
    def update_path_to_player(self, player_pos, playable_area_grid):
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
                # Reconstruct the path
                path = []
                while current_point:
                    path.append(current_point)
                    current_point = came_from[current_point]
                self.path = path[::-1]
                return

            for move in moves:
                new_point = (current_point[0] + move[0], current_point[1] + move[1])

                if (
                        0 <= new_point[0] < len(playable_area_grid[0])
                        and 0 <= new_point[1] < len(playable_area_grid)
                        and not playable_area_grid[new_point[1]][new_point[0]]
                ):
                    new_cost = cost_to_point[current_point] + 1
                    if (
                            new_point not in cost_to_point
                            or new_cost < cost_to_point[new_point]
                    ):
                        cost_to_point[new_point] = new_cost
                        priority = (new_cost + self.heuristic(new_point, goal), new_point)
                        heapq.heappush(open_set, priority)
                        came_from[new_point] = current_point

        self.path = []

    def heuristic(self, a, b):
        return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

    def move_towards_player_astar(self, playable_area_grid):
        if self.path:
            for next_point in reversed(self.path):
                target_x = next_point[0] * self.grid_size + self.grid_size / 2
                target_y = next_point[1] * self.grid_size + self.grid_size / 2

                direction = pygame.math.Vector2(target_x - self.rect.x, target_y - self.rect.y).normalize()
                new_rect = self.rect.move(direction.x * self.speed, direction.y * self.speed)

                grid_x = int(new_rect.x / self.grid_size)
                grid_y = int(new_rect.y / self.grid_size)

                if (
                        0 <= grid_x < len(playable_area_grid[0])
                        and 0 <= grid_y < len(playable_area_grid)
                        and not playable_area_grid[grid_y][grid_x]
                ):
                    self.rect = new_rect
                    break
    
    def draw_health_bar(self):
        health_ratio = self.health / 2  # Assuming max health is 2
        bar_width = 40
        bar_height = 5
        health_bar_width = int(bar_width * health_ratio)
        health_bar_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(health_bar_surface, (255, 255, 255), (0, 0, bar_width, bar_height))
        
        if health_ratio > 0.6:
            color = (0, 255, 0)
        elif health_ratio > 0.3:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
            
        pygame.draw.rect(health_bar_surface, color, (0, 0, health_bar_width, bar_height))
        health_bar_pos = (self.rect.centerx - bar_width // 2, self.rect.y - 10)
        screen.blit(health_bar_surface, health_bar_pos)
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            # Spawn blood drop at enemy location instead of directly adding to player
            blood_drop = BloodDrop(self.rect.centerx, self.rect.centery, self.blood_value)
            pickup_group.add(blood_drop)
            all_sprites_group.add(blood_drop)
            self.kill()
        else:
            # Removing this line or comment it out to ensure enemies continue hunting
            # In dodge stste they would exit the screen 
            # self.change_state("dodge" if random.random() > 0.5 else "recover")
            
            # Keep the enemy in "hunt" state after taking damage
            self.state = "hunt"
    
    def change_state(self, new_state):
        self.state = new_state
        self.state_timer = random.randint(60, 120)  # 1-2 seconds at 60 FPS
    
    def update(self):
        if not self.spawned:
            self.spawn_randomly(player.playable_area_grid, player.pos, 150)
        else:
            # State machine behavior
            if self.state == "hunt":
                # Normal hunting behavior
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
                # Stand still and recover
                pass
                
            # Update state timer
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.change_state("hunt")  # Return to hunting state

            # Update rotation to face player
            self.update_rotation(player.pos.x, player.pos.y)
            
            # Draw health bar
            self.draw_health_bar()
            
            # Check collision with player
            if self.rect.colliderect(player.hitbox_rect) and not player.invincible:
                player.health -= 1
                player.invincible = True
                player.invincibility_timer = 60  # 1 second at 60 FPS

# Add a new VampireLord class for the final boss
class VampireLord(BaseEnemy):
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
        self.active_minions = 0  # Track how many minions are active
        self.max_minions = 3     # Maximum number of minions allowed
        
    def update(self):
        if not self.spawned:
            # Boss always spawns in the grand hall center
            self.rect.center = (610, 330)  # Center of grand hall coordinates
            self.spawned = True
        else:
            # Update boss behavior based on health/phase
            if self.health > 5:  # Phase 1
                self.phase = 1
                self.phase_one_behavior()
            elif self.health > 2:  # Phase 2
                if self.phase == 1:  # Transition to phase 2
                    show_story_text("The vampire lord transforms into a giant bat!", 2000)
                    # Change appearance for phase 2
                    self.base_image = pygame.transform.rotozoom(self.base_image, 0, 1.2)
                self.phase = 2
                self.phase_two_behavior()
            else:  # Phase 3
                if self.phase == 2:  # Transition to phase 3
                    show_story_text("The vampire lord enters a blood rage!", 2000)
                    # Change appearance for phase 3
                    red_overlay = pygame.Surface(self.base_image.get_size(), pygame.SRCALPHA)
                    red_overlay.fill((255, 0, 0, 100))
                    self.base_image.blit(red_overlay, (0, 0))
                self.phase = 3
                self.phase_three_behavior()
            
            # Always update rotation to face player
            self.update_rotation(player.pos.x, player.pos.y)
            
            # Draw health bar
            self.draw_health_bar()
            
            # Check collision with player
            if self.rect.colliderect(player.hitbox_rect) and not player.invincible:
                player.health -= 1
                player.invincible = True
                player.invincibility_timer = 60  # 1 second at 60 FPS
    
    def phase_one_behavior(self):
        # Keep distance and summon minions
        # Move away from player if too close
        distance_to_player = pygame.math.Vector2(self.rect.centerx - player.pos.x, 
                                              self.rect.centery - player.pos.y).length()
        
        if distance_to_player < 200:
            direction = pygame.math.Vector2(self.rect.centerx - player.pos.x, 
                                         self.rect.centery - player.pos.y).normalize()
            new_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery) + direction * self.speed
            if is_within_playable_area(new_pos):
                self.rect.center = new_pos
                
        # Count current minions (ghouls)
        self.active_minions = len([e for e in enemy_group if isinstance(e, Ghoul)])
        
        # Summon minions occasionally, but only if below the maximum
        if self.summon_cooldown <= 0 and self.active_minions < self.max_minions:
            ghoul = Ghoul()
            ghoul.rect.center = self.rect.center
            ghoul.spawned = True
            enemy_group.add(ghoul)
            all_sprites_group.add(ghoul)
            self.summon_cooldown = 180  # 3 seconds
        else:
            self.summon_cooldown -= 1
    
    def phase_two_behavior(self):
        # Bat form - faster movement and swooping attacks
        self.speed = 4
        
        # Path planning
        if random.random() < 0.02:  # Occasionally recalculate path
            angle = random.randint(0, 360)
            direction = pygame.math.Vector2(math.cos(math.radians(angle)), 
                                         math.sin(math.radians(angle))).normalize()
            target_pos = pygame.math.Vector2(player.pos.x, player.pos.y) + direction * 200
            
            # If position is valid, move towards it
            if is_within_playable_area(target_pos):
                # Calculate path to this position
                self.update_path_to_player(target_pos, player.playable_area_grid)
        
        # Follow path if one exists
        if hasattr(self, 'path') and self.path:
            self.move_towards_player_astar(player.playable_area_grid)
        
        # Swoop attack when in line with player
        if self.attack_cooldown <= 0:
            # Direct charge toward player
            self.speed = 8
            direction = pygame.math.Vector2(player.pos.x - self.rect.centerx, 
                                         player.pos.y - self.rect.centery).normalize()
            new_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery) + direction * self.speed
            if is_within_playable_area(new_pos):
                self.rect.center = new_pos
            self.attack_cooldown = 120  # 2 seconds
        else:
            self.attack_cooldown -= 1
            if self.attack_cooldown == 60:  # Reset speed halfway through cooldown
                self.speed = 4
    
    def phase_three_behavior(self):
        # Blood rage - aggressive teleportation and attacks
        self.speed = 5
        
        # Don't summon minions in this phase - focus on direct attacks
        
        # Teleport frequently
        if self.teleport_cooldown <= 0:
            # Teleport to random position near player
            angle = random.randint(0, 360)
            direction = pygame.math.Vector2(math.cos(math.radians(angle)), 
                                        math.sin(math.radians(angle))).normalize()
            teleport_pos = pygame.math.Vector2(player.pos.x, player.pos.y) + direction * 100
            
            if is_within_playable_area(teleport_pos):
                self.rect.center = teleport_pos
            self.teleport_cooldown = 60  # 1 second
        else:
            self.teleport_cooldown -= 1


# Bat Enemy
class Ghoul(BaseEnemy):
    def __init__(self):
        original_image_path = "images/ghoul.png"
        tiny_image = pygame.image.load(original_image_path).convert_alpha()
        tiny_image = pygame.transform.scale(tiny_image, (20, 20))  # Set appropriate small size

        # Now pass the pre-scaled image to BaseEnemy
        super().__init__(original_image_path, health=2, speed=2)
        self.image = tiny_image
        self.rect = self.image.get_rect(center=self.rect.center)  # Keep position centered
        self.blood_value = 10


        

class Vampire(BaseEnemy):
    def __init__(self):
        super().__init__("images/vampire_enemy.png", health=3, speed=3)
        self.blood_value = 20
        self.can_teleport = True
        self.teleport_cooldown = 0
        
    def update(self):
        super().update()
        
        # Special teleport ability
        if self.can_teleport and self.teleport_cooldown <= 0:
            distance_to_player = pygame.math.Vector2(self.rect.centerx - player.pos.x, self.rect.centery - player.pos.y).length()
            if distance_to_player < 200 and distance_to_player > 100:
                # Teleport behind player
                behind_player = player.pos - pygame.math.Vector2(30, 0).rotate(player.angle)
                if is_within_playable_area(behind_player):
                    self.rect.center = behind_player
                    self.teleport_cooldown = 180  # 3 seconds cooldown
        
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1


class Werewolf(BaseEnemy):
    def __init__(self):
        super().__init__("images/warewolf.png", health=4, speed=4)
        self.blood_value = 30
        self.enraged = False
        
    def update(self):
        super().update()
        
        # Enrage when health is low
        if self.health <= 2 and not self.enraged:
            self.enraged = True
            self.speed = 6  # Faster when enraged
            self.base_image = pygame.transform.rotozoom(self.base_image, 0, 1.2)  # Slightly larger


# Function to show boss introduction
def show_boss_intro():
    boss_intro_text = "The vampire lord appears! Defeat him to rescue your beloved!"
    
    # Create dramatic effect with screen flash
    for _ in range(3):
        # Flash screen red
        overlay = pygame.Surface((800, 700))
        overlay.fill((150, 0, 0))
        screen.blit(overlay, (0, 0))
        pygame.display.update()
        pygame.time.delay(100)
        
        # Return to normal
        screen.blit(background, (0, 0))
        all_sprites_group.draw(screen)
        pygame.display.update()
        pygame.time.delay(100)
    
    # Show boss text
    show_story_text(story_events["boss"], 3000)

# Function to spawn enemies
def spawn_enemies(wave_number):
    enemies = pygame.sprite.Group()
    
    if wave_number <= MAX_WAVES:
        # Basic ghouls for all waves 
        if wave_number == 3:
            num_ghouls = 3  
        else:
            num_ghouls = wave_number * 2
            
        for i in range(num_ghouls):
            enemy = Ghoul()
            if wave_number == 3:  # Make ghouls weaker in wave 3
                enemy.health = 1
                enemy.speed = 1.5
                enemy.blood_value = 15  # More blood essence
            enemy_group.add(enemy)
            all_sprites_group.add(enemy)
            enemies.add(enemy)
        
        # Add vampires from wave 2
        if wave_number >= 2:
            if wave_number == 3:
                num_vampires = 1  # Only 1 vampire in wave 3
            else:
                num_vampires = wave_number - 1
                
            for i in range(num_vampires):
                enemy = Vampire()
                if wave_number == 3:  # Make vampires weaker in wave 3
                    enemy.health = 2
                    enemy.speed = 2
                    enemy.teleport_cooldown = 300  # Longer cooldown between teleports
                    enemy.blood_value = 30  # More blood essence
                enemy_group.add(enemy)
                all_sprites_group.add(enemy)
                enemies.add(enemy)
                
        # Add werewolves in wave 3 - make it weaker
        if wave_number == 3:
            enemy = Werewolf()
            enemy.health = 2 
            enemy.speed = 3   
            enemy.blood_value = 50  # More blood essence to prepare for boss
            enemy_group.add(enemy)
            all_sprites_group.add(enemy)
            enemies.add(enemy)
    
    elif wave_number == MAX_WAVES + 1:  # Boss wave
        # Spawn boss
        show_boss_intro()
        boss = VampireLord()
        enemy_group.add(boss)
        all_sprites_group.add(boss)
        enemies.add(boss)

    return enemies


def show_upgrades():
    # Show 3 random upgrades for the player to choose from
    upgrades = [
       # {"name": "Dash Ability", "description": "Quick dash in direction of movement", "effect": "dash"},
        {"name": "Mist Form", "description": "Temporary invincibility", "effect": "mist"},
        {"name": "Bat Transform", "description": "Increased speed for a short time", "effect": "bat"},
        {"name": "Blood Capacity", "description": "Increase max blood essence", "effect": "blood"},
        {"name": "Health Up", "description": "Gain an extra heart", "effect": "health"}
    ]
    
    # Filter out upgrades player already has
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
    
    # Choose 3 random upgrades
    if len(available_upgrades) > 3:
        chosen_upgrades = random.sample(available_upgrades, 3)
    else:
        chosen_upgrades = available_upgrades
    
    # Display the upgrades
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    title_text = font.render("Choose an Upgrade", True, (200, 0, 0))
    screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 100))
    
    for i, upgrade in enumerate(chosen_upgrades):
        pygame.draw.rect(screen, (50, 0, 0), (150 + i*200, 200, 150, 200))
        pygame.draw.rect(screen, (100, 0, 0), (150 + i*200, 200, 150, 200), 2)
        
        name_text = font.render(upgrade["name"], True, (200, 200, 200))
        screen.blit(name_text, (150 + i*200 + 75 - name_text.get_width() // 2, 220))
        
        desc_text = small_font.render(upgrade["description"], True, (200, 200, 200))
        screen.blit(desc_text, (150 + i*200 + 75 - desc_text.get_width() // 2, 280))
        
        key_text = font.render(f"Press {i+1}", True, (200, 200, 200))
        screen.blit(key_text, (150 + i*200 + 75 - key_text.get_width() // 2, 350))
    
    pygame.display.update()
    
    # Wait for player choice
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
    
    # Apply the selected upgrade
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


def victory_screen():
    # Switch to rescue background showing the reunion
    screen.blit(rescue_background, (0, 0))
    
    # Add a semi-transparent overlay
    overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))
    
    # Show victory message
    font = pygame.font.Font(None, 72)
    victory_text = font.render('You Have Prevailed!', True, (200, 0, 0))
    text_rect = victory_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100))
    screen.blit(victory_text, text_rect)
    
    # Show reunion message
    message_font = pygame.font.Font(None, 36)
    message_text = message_font.render('You have rescued your beloved from the vampire lord.', True, (200, 200, 200))
    message_rect = message_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(message_text, message_rect)
    
    # Draw player and partner together
    partner_rect = partner_image.get_rect(center=(screen.get_width() // 2 - 50, screen.get_height() // 2 + 100))
    player_rect = player.image.get_rect(center=(screen.get_width() // 2 + 50, screen.get_height() // 2 + 100))
    screen.blit(partner_image, partner_rect)
    screen.blit(player.image, player_rect)
    
    # Display retry message
    retry_font = pygame.font.Font(None, 30)
    retry_text = retry_font.render('Press Space to Play Again or Escape to Quit', True, (200, 200, 200))
    retry_rect = retry_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 200))
    screen.blit(retry_text, retry_rect)
    
    pygame.display.update()
    pygame.mixer.Channel(1).stop()
    # Play victory music if available, otherwise use menu music
    pygame.mixer.Channel(0).play(menu_sound, loops=-1)
    
    # Wait for player input
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
    
    return replay  # Return True to replay or False to quit

def game_over_screen(wave_number):
    screen.blit(background, (0, 0))
    overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    # Display you died message
    font = pygame.font.Font(None, 72)
    game_over_text = font.render('The Darkness Claims You', True, (150, 0, 0))
    
    # Ensure text fits
    if game_over_text.get_width() > screen.get_width() - 60:
        font = pygame.font.Font(None, 60)
        game_over_text = font.render('The Darkness Claims You', True, (150, 0, 0))
    
    text_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 80))
    screen.blit(game_over_text, text_rect)

    # Display wave number
    wave_font = pygame.font.Font(None, 36)
    wave_text = wave_font.render(f'You survived {wave_number} waves', True, (200, 200, 200))
    wave_rect = wave_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(wave_text, wave_rect)

    # Display retry message
    retry_font = pygame.font.Font(None, 30)
    retry_text = retry_font.render('Press Space to Retry', True, (200, 200, 200))
    retry_rect = retry_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 80))
    screen.blit(retry_text, retry_rect)

    pygame.display.update()
    pygame.mixer.Channel(1).stop()
    pygame.mixer.Channel(0).play(menu_sound, loops=-1)

    # Wait for the player to press space to retry
    space_pressed = False
    while not space_pressed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                space_pressed = True

    # Kill all enemies before retrying
    for enemy in enemy_group.sprites():
        enemy.kill()

    pygame.mixer.Channel(0).stop()
    pygame.mixer.Channel(1).play(background_music, loops=-1)
    return True  # Retry the game


def show_story_text(text, duration=3000):
    font = pygame.font.Font(None, 36)
    
    # Split text into multiple lines if too long
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, (200, 200, 200))
        
        # If adding this word makes the line too long, start a new line
        if test_surface.get_width() > screen.get_width() - 100:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    
    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))
    
    # Create a surface tall enough for all lines
    line_height = font.get_linesize()
    text_height = line_height * len(lines)
    
    # Create surfaces for text and background
    text_surfaces = []
    max_width = 0
    
    for line in lines:
        text_surface = font.render(line, True, (200, 200, 200))
        text_surfaces.append(text_surface)
        max_width = max(max_width, text_surface.get_width())
    
    # Create background surface
    overlay = pygame.Surface((max_width + 40, text_height + 40), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    
    # Position at bottom of screen with padding
    overlay_y = screen.get_height() - text_height - 60
    screen.blit(overlay, ((screen.get_width() - max_width - 40) // 2, overlay_y))
    
    # Draw each line
    for i, text_surface in enumerate(text_surfaces):
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, overlay_y + 20 + i * line_height))
        screen.blit(text_surface, text_rect)
    
    pygame.display.update()
    
    pygame.time.set_timer(pygame.USEREVENT + 1, duration)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.USEREVENT + 1:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                waiting = False


def show_area_transition(area_name):
    font = pygame.font.Font(None, 48)
    text_surface = font.render(f"Entering: {area_name}", True, (150, 0, 0))
    
    # Make sure text fits within screen width
    if text_surface.get_width() > screen.get_width() - 60:
        # If too long, use smaller font
        font = pygame.font.Font(None, 36)
        text_surface = font.render(f"Entering: {area_name}", True, (150, 0, 0))
    
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    
    # Fade in
    for alpha in range(0, 255, 5):
        screen.blit(background, (0, 0))
        all_sprites_group.draw(screen)
        
        overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        
        # Create copy of text_surface with new alpha
        alpha_surface = text_surface.copy()
        alpha_surface.set_alpha(alpha)
        screen.blit(alpha_surface, text_rect)
        pygame.display.update()
        pygame.time.delay(10)
    
    pygame.time.delay(1000)
    
    # Fade out
    for alpha in range(255, 0, -5):
        screen.blit(background, (0, 0))
        all_sprites_group.draw(screen)
        
        overlay = pygame.Surface((800, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        
        # Create copy of text_surface with new alpha
        alpha_surface = text_surface.copy()
        alpha_surface.set_alpha(alpha)
        screen.blit(alpha_surface, text_rect)
        pygame.display.update()
        pygame.time.delay(10)

# Setup sprite groups
all_sprites_group = pygame.sprite.Group()
attack_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
pickup_group = pygame.sprite.Group()

# Create player instance
player = Player()
all_sprites_group.add(player)

# Game state
current_wave = 1
room_cleared = False
enemies = spawn_enemies(current_wave)
show_minimap = False
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

# MAIN GAME LOOP
running = True
show_menu = True
wave_transition_timer = 0
waiting_for_next_wave = False

while running:
    if show_menu:
        start_menu()
        show_menu = False
        # Show initial story text
        show_story_text(story_events[1])
    
    # Fill screen with background
    screen.blit(background, (0, 0))

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                show_minimap = not show_minimap
        elif event.type == pygame.USEREVENT:
            # Event for bat transformation ending
            player.speed = 5  # Reset speed after bat transformation

    # Display wave and room information
    font = pygame.font.Font(None, 36)
    wave_text = font.render(f'Wave: {current_wave}', True, (200, 200, 200))
    screen.blit(wave_text, (10, 60))  # Changed from (10, 10) to (10, 60)
    
    # Check if player entered a new area
    if player.current_room not in discovered_areas:
        discovered_areas.add(player.current_room)
        #show_area_transition(area_descriptions[player.current_room])
    
    # Update attacks
    for attack in attack_group.sprites():
        attack.update()
    
    # Check if all enemies are killed - only process this if not already waiting for next wave
    if len(enemy_group) == 0 and not room_cleared and not waiting_for_next_wave:
        if current_wave > MAX_WAVES:  # If we've defeated the boss
            # Show victory screen
            if victory_screen():
                # Reset game for replay
                player.health = player.max_health
                player.blood_essence.current = 50
                player.blood_essence.maximum = 100
                player.has_dash = False
                player.has_mist_form = False
                player.has_bat_transform = False
                current_wave = 1
                room_cleared = False
                enemies = spawn_enemies(current_wave)
                discovered_areas = set(["entrance"])
            else:
                running = False
        else:
            room_cleared = True
            waiting_for_next_wave = True
            wave_transition_timer = 60  # 1 second delay at 60 FPS
    
    # Process wave transition timer if waiting for next wave
    if waiting_for_next_wave:
        wave_transition_timer -= 1
        if wave_transition_timer <= 0:
            # Show story event if applicable
            if current_wave in story_events:
                show_story_text(story_events[current_wave])
            
            # Check if we've reached max waves
            if current_wave == MAX_WAVES:
                # Spawn boss after final wave
                current_wave += 1
                enemies = spawn_enemies(current_wave)  # This will spawn the boss
                room_cleared = False
                waiting_for_next_wave = False
            elif current_wave < MAX_WAVES:
                # Offer upgrades after each wave
                chosen_upgrade = show_upgrades()
                if chosen_upgrade:
                    show_story_text(f"New ability gained: {chosen_upgrade.replace('_', ' ').title()}")
                
                # Prepare next wave
                current_wave += 1
                enemies = spawn_enemies(current_wave)
                room_cleared = False
                waiting_for_next_wave = False
    
    # Draw minimap if enabled
    if show_minimap:
        minimap_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        minimap_surface.fill((0, 0, 0, 150))
        
        # Draw room layout
        rooms = create_room_layout()
        for room_name, room_rect in rooms.items():
            # Scale down room coordinates for minimap
            mini_rect = pygame.Rect(
                room_rect.x // 4 + 10, 
                room_rect.y // 4 + 10, 
                room_rect.width // 4, 
                room_rect.height // 4
            )
            
            # Color depends on if room is discovered
            if room_name in discovered_areas:
                pygame.draw.rect(minimap_surface, (100, 0, 0), mini_rect)
            else:
                pygame.draw.rect(minimap_surface, (50, 50, 50), mini_rect)
            
            # Highlight current room
            if room_name == player.current_room:
                pygame.draw.rect(minimap_surface, (150, 0, 0), mini_rect, 2)
        
        # Draw player position on minimap
        player_mini_pos = (player.pos.x // 4 + 10, player.pos.y // 4 + 10)
        pygame.draw.circle(minimap_surface, (255, 255, 255), player_mini_pos, 3)
        
        # Draw enemies on minimap
        for enemy in enemy_group:
            enemy_mini_pos = (enemy.rect.centerx // 4 + 10, enemy.rect.centery // 4 + 10)
            pygame.draw.circle(minimap_surface, (255, 0, 0), enemy_mini_pos, 2)
        
        screen.blit(minimap_surface, (screen.get_width() - 210, screen.get_height() - 210))
    
    # Update and draw all sprites
    all_sprites_group.draw(screen)
    all_sprites_group.update()

    for pickup in pickup_group:
        pickup.update()
    
    # Check if player's health is zero or less
    if player.health <= 0:
        # Display game over screen
        if game_over_screen(current_wave):
            # Reset game state
            player.health = player.max_health
            player.blood_essence.current = 50
            player.blood_essence.maximum = 100
            player.has_dash = False
            player.has_mist_form = False
            player.has_bat_transform = False
            current_wave = 1
            room_cleared = False
            enemies = spawn_enemies(current_wave)
            discovered_areas = set(["entrance"])
        else:
            running = False
    
    pygame.display.update()
    clock.tick(60)  # 60 FPS