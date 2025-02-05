import pygame
import math
from random import randint, choice

pygame.init()

# Game setup
window_width, window_height = 1280, 720
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Dodge Game')
clock = pygame.time.Clock()
running, game_status = True, 'playing'

# Game player setup/variables
max_health = 10
player_health = max_health
player_speed, laser_speed, meteor_speed = 0.5, 0.75, 0.4
last_teleport_time, teleport_cooldown = 0, 5 * 1000 # in milliseconds
multiplier = 1.5

# Health bar variables
bar_width, bar_height, offset, scale = 100, 10, -20, 0.5

# Sprite setup
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (111*0.8, 90*0.8))
        self.rect = self.image.get_frect(center = (window_width / 2, window_height / 2))
        self.position = pygame.Vector2(self.rect.center)
        self.keep_moving = False

    def update(self, mouse_click, pos, speed):
        # Teleport on left click
        if mouse_click[0] and (current_time - last_teleport_time ) >= teleport_cooldown:
            self.teleport()
        # Redefine target location on right click
        if mouse_click[2]:
            self.target = pygame.Vector2(pos)
            self.keep_moving = True
        # Continue moving to target until arrive
        if self.keep_moving:
            self.movement(delta_time, speed)

    def teleport(self):
        global last_teleport_time
        self.target = pygame.Vector2(pygame.mouse.get_pos())
        last_teleport_time = pygame.time.get_ticks()
        player.check_boundary(self.target.x, self.target.y)

    def movement(self, dt, speed):
        x, y = self.position.x, self.position.y
        x_delta, y_delta = self.target.x - x, self.target.y - y

        # Calculate Angle
        angle = math.atan2(-y_delta, x_delta)

        movement = speed * dt
        x += movement * math.cos(angle)
        y -= movement * math.sin(angle)   

        if abs(x_delta) < 1 and abs(y_delta) < 1: 
            self.keep_moving = False
        else:
            player.check_boundary(x, y)

    def check_boundary(self, x, y):
        # Check if action is within the screen, then move
        self.position.x = max(self.image.get_width() / 2, min(window_width - self.image.get_width() / 2, x))
        self.position.y = max(self.image.get_height() / 2, min(window_height - self.image.get_height() / 2, y))
        self.rect.center = (x, y)

class Camera(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('RedSpace.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (window_width, window_height))
        self.rect = self.image.get_frect(center = (window_width / 2, window_height / 2))
        
class Laser(pygame.sprite.Sprite):
    def __init__(self, surface, position, speed, groups):
        super().__init__(groups)
        self.image, self.speed = surface, speed
        self.rect = self.image.get_frect(midbottom = position)

        self.spawn_edge = choice(['top', 'bottom', 'left', 'right'])

        # Set starting position based on the edge
        if self.spawn_edge == 'top':
            self.position = pygame.Vector2(randint(0, window_width), 0)
            self.target = pygame.Vector2(randint(0, window_width), window_height)
        elif self.spawn_edge == 'bottom':
            self.position = pygame.Vector2(randint(0, window_width), window_height)
            self.target = pygame.Vector2(randint(0, window_width), 0)
        elif self.spawn_edge == 'left':
            self.position = pygame.Vector2(0, randint(0, window_height))
            self.target = pygame.Vector2(window_width, randint(0, window_height))
        elif self.spawn_edge == 'right':
            self.position = pygame.Vector2(window_width, randint(0, window_height))
            self.target = pygame.Vector2(0, randint(0, window_height))

        self.rect.center = self.position

        # Calculate the angle only when the laser is created
        self.angle = self.calculate_angle()

        # Rotate the laser image to match its movement direction
        self.rotate(math.pi / 2 - self.angle)

    def calculate_angle(self):
        x, y = self.position.x, self.position.y
        x_delta, y_delta = self.target.x - x, self.target.y - y
        angle = math.atan2(-y_delta, x_delta)
        return angle

    def move(self, dt):
        x, y = self.position.x, self.position.y

        # Move the laser in the calculated direction
        movement = self.speed * dt
        x += movement * math.cos(self.angle)
        y -= movement * math.sin(self.angle)

        self.position.x, self.position.y = x, y
        self.rect.center = (x, y)

        # Check if the laser has gone off the screen, and if so, remove it
        if (self.rect.bottom < 0 or self.rect.top > window_height or self.rect.right < 0 or self.rect.left > window_width):
            self.kill()

    def rotate(self, angle):
        # Rotate the laser image by the calculated angle
        rotated_image = pygame.transform.rotate(self.image, -math.degrees(angle))
        self.rect = rotated_image.get_frect(center=self.rect.center)
        self.image = rotated_image

def display_score(time):
    text_surface = font.render(str(time // 10), True, (240, 240, 240))
    text_rect = text_surface.get_frect(midbottom = (window_width / 2, window_height - 50))
    screen.blit(text_surface, text_rect)

def health_bar(player):
    x, y = player.rect.centerx, player.rect.top
    pygame.draw.rect(screen, (255, 150, 150), (x - bar_width / 2, y + offset, bar_width, bar_height))
    pygame.draw.rect(screen, (144, 238, 144), (x - bar_width / 2, y + offset, bar_width * (player_health / max_health), bar_height))
    
    # Draw and scale text
    health_text = font.render(f'{player_health} / {max_health}', True, (240, 240, 240))
    health_text = pygame.transform.scale(health_text, (int(health_text.get_width() * scale), int(health_text.get_height() * scale)))
    screen.blit(health_text, (x - health_text.get_width() / 2, y + offset - bar_height ))

def game_over_screen():
    end_screen_surface.fill((213, 211, 211, 1))
    screen.blit(end_screen_surface, (0, 0))

    # Render text
    game_over_text = font.render("Game Over!", True, (255, 0, 0))
    game_over_rect = game_over_text.get_frect(center = (window_width / 2, window_height / 2))
    screen.blit(game_over_text, game_over_rect)

# Add surfaces with multiple instances
laser_surface = pygame.image.load('laser.png').convert_alpha()
laser_surface = pygame.transform.scale2x(laser_surface)
meteor_surface = pygame.image.load('meteor.png').convert_alpha()
end_screen_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
# Font type
font = pygame.font.Font('Oxanium-Bold.ttf', 40)

# Add laser and meteor events
laser_event = pygame.event.custom_type()
pygame.time.set_timer(laser_event, 1000)
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 1500)
speed_up_event = pygame.event.custom_type()
pygame.time.set_timer(speed_up_event, 20000)
power_up_event = pygame.event.custom_type()
pygame.time.set_timer(power_up_event, 30000)

# Sprite intialization
all_sprites, object_sprites = pygame.sprite.Group(), pygame.sprite.Group()
camera = Camera(all_sprites)
player = Player(all_sprites)

while running:
    # Clock setup for framerate independence
    delta_time = clock.tick()
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == laser_event:
            Laser(laser_surface, (randint(0, window_width), window_height), laser_speed, (all_sprites, object_sprites))
        if event.type == meteor_event:
            Laser(meteor_surface, (randint(0, window_width), window_height), meteor_speed, (all_sprites, object_sprites))
        if event.type == speed_up_event:
            player_speed, laser_speed, meteor_speed, multiplier = player_speed + 0.1, laser_speed + 0.2, meteor_speed + 0.15, multiplier + 0.25
            pygame.time.set_timer(laser_event, int(1000 // multiplier))
            pygame.time.set_timer(meteor_event, int(1500 // multiplier))
    
    if game_status == 'playing':
        # Check for mouse input
        mouse_click = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # Draw and update all objects
        for laser in object_sprites:
            laser.move(delta_time)
        
        Player.update(player, mouse_click, mouse_pos, player_speed)

        # Check for collisions
        if pygame.sprite.spritecollide(player, object_sprites, True, pygame.sprite.collide_mask):
            player_health -= 1
            if player_health == 0:
                game_status = 'over'
                # Stop timers when the game is over
                for event in [laser_event, meteor_event, speed_up_event]:
                    pygame.time.set_timer(event, 0)

        # Draw screen, health bar, and score
        all_sprites.draw(screen)
        health_bar(player)
        display_score(current_time)

    if game_status == 'over':
        game_over_screen()

    pygame.display.update()

pygame.quit()