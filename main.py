import math
import os
import time
import pygame
import numpy as np 
from dotenv import load_dotenv
from src import map, raycast, mcl, lidar

load_dotenv()

# Setup
pygame.init()

i = 0
j = 0
init_time = time.time()

PLAYER = 1
TEST_PARTICLE = 2

SCREEN_HEIGHT = int(os.getenv("SCREEN_HEIGHT",720))
SCREEN_WIDTH  = int(os.getenv("SCREEN_WIDTH",1280))
SCREEN_COLOR  = os.getenv("SCREEN_COLOR","black")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0

print(os.getenv("MAP"))
field = map.load_map(screen, os.path.join("maps/",str(os.getenv("MAP"))))
particles = mcl.MCLInterface(1000, field)


# calculate mid point of starting rect
player_pos_x = (2 * field.starting_rect['x_min'] + field.starting_rect['width']) / 2
player_pos_y = (2 * field.starting_rect['y_min'] + field.starting_rect['height']) / 2

player_pos = pygame.Vector2(player_pos_x, player_pos_y)
test_pos = pygame.Vector2(player_pos_x, player_pos_x)
player_angle = math.radians(-90)
test_angle = math.radians(-90)

lidar = lidar.Lidar(np.array([player_pos_x, player_pos_y, player_angle]), field, 3, 4)

player_radius = 20
X_t_minus_1 = [player_pos_x, player_pos_y, player_angle]
X_t = np.copy(X_t_minus_1)


# Game loop
player = PLAYER
while running:
    
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_q]:
            running = False

    if keys[pygame.K_1]:
        player = PLAYER
    if keys[pygame.K_2]:
        player = TEST_PARTICLE
            
    screen.fill(SCREEN_COLOR)
    if player == PLAYER:
        # handle keyboard input     
        if keys[pygame.K_w]:
            player_pos.y += 200 * dt * math.sin(player_angle)
            player_pos.x += 200 * dt * math.cos(player_angle)
            X_t[1] += 200 * dt * math.sin(X_t[2])
            X_t[0] += 200 * dt * math.cos(X_t[2])
        if keys[pygame.K_s]:
            player_pos.y -= 200 * dt * math.sin(player_angle)
            player_pos.x -= 200 * dt * math.cos(player_angle)
            X_t[1] -= 200 * dt * math.sin(X_t[2])
            X_t[0] -= 200 * dt * math.cos(X_t[2])
        if keys[pygame.K_a]:
            player_pos.x += 200 * dt * math.sin(player_angle)
            player_pos.y -= 200 * dt * math.cos(player_angle) 
            X_t[0] += 200 * dt * math.sin(X_t[2])
            X_t[1] -= 200 * dt * math.cos(X_t[2]) 
        if keys[pygame.K_d]:
            player_pos.x -= 200 * dt * math.sin(player_angle)
            player_pos.y += 200 * dt * math.cos(player_angle)
            X_t[0] -= 200 * dt * math.sin(X_t[2])
            X_t[1] += 200 * dt * math.cos(X_t[2])
        if keys[pygame.K_j]:
            player_angle -= (math.pi) * 1.2 * dt
            X_t[2] -= (math.pi) * 1.2 * dt
        if keys[pygame.K_k]:
            player_angle += (math.pi) * 1.2 * dt
            X_t[2] += (math.pi) * 1.2 * dt
    else: # player is test particle
        if keys[pygame.K_w]:
            test_pos.y += 200 * dt * math.sin(player_angle)
            test_pos.x += 200 * dt * math.cos(player_angle)
        if keys[pygame.K_s]:
            test_pos.y -= 200 * dt * math.sin(player_angle)
            test_pos.x -= 200 * dt * math.cos(player_angle)
        if keys[pygame.K_a]:
            test_pos.x += 200 * dt * math.sin(player_angle)
            test_pos.y -= 200 * dt * math.cos(player_angle) 
        if keys[pygame.K_d]:
            test_pos.x -= 200 * dt * math.sin(player_angle)
            test_pos.y += 200 * dt * math.cos(player_angle)
        if keys[pygame.K_j]:
            test_angle -= (math.pi) * 1.2 * dt
        if keys[pygame.K_k]:
            test_angle += (math.pi) * 1.2 * dt

        
    pygame.draw.circle(screen, "red", player_pos, player_radius)
    # draw player's orientation
    player_head_x = player_pos.x + player_radius * math.cos(player_angle)
    player_head_y = player_pos.y + player_radius * math.sin(player_angle)
    pygame.draw.line(screen, "purple", player_pos, pygame.Vector2(player_head_x, player_head_y), 5)
    
    # rays = raycast.compute_rays(5, player_pos, player_angle, map)
    # raycast.draw_rays(screen, "yellow", player_pos, rays, 3)
    
    map.draw_map(screen, "blue", field, 3)
    control = np.stack((X_t_minus_1, X_t))
    lidar.state = np.array([player_pos.x, player_pos.y, player_angle])
    measurement = lidar.measurements
    
    particles.update(control, measurement)
    lidar.draw_measurements(screen, "yellow", 2)
    particles.draw_particles(screen, "red", 10)
    particles.draw_state_estimation(screen, "green", player_radius)
    
    X_t_minus_1 = np.copy(X_t)

    pygame.display.flip()
    
    dt = clock.tick(60) / 1000
    
    d_time = time.time() - init_time
    j += 1
    d_i = j - i
    if d_time >= 1:
        init_time = time.time()
        i = j
        refresh_rate = d_i / d_time 
        print(f'Refresh_rate = {refresh_rate:.2f} Hz')
        
    
pygame.quit()
