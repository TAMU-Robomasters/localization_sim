"""Use 'wasd' to move around. Use 'j' and 'k' to rotate. Press 'q' to stop program"""
import math
import os
import time
import pygame
import numpy as np 
from dotenv import load_dotenv
from src import map, raycast, mcl, lidar, pathfinder
load_dotenv()

# Setup
pygame.init()

# Constants
MAX_FPS = 60
SCREEN_HEIGHT = int(os.getenv("SCREEN_HEIGHT",720))
SCREEN_WIDTH  = int(os.getenv("SCREEN_WIDTH",1280))
SCREEN_COLOR  = os.getenv("SCREEN_COLOR","black")

# Pygame 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

# Init classes from local packages
field = map.load_map(screen, os.path.join("maps/",str(os.getenv("MAP"))))

robot_pos_x = (2 * field.starting_rect['x_min'] + field.starting_rect['width']) / 2
robot_pos_y = (2 * field.starting_rect['y_min'] + field.starting_rect['height']) / 2
robot_pos = pygame.Vector2(robot_pos_x, robot_pos_y)
robot_angle = math.radians(-90)
robot_radius = 20
lidar = lidar.Lidar(np.array([robot_pos_x, robot_pos_y, robot_angle]), field, 3, 4)

particles = mcl.MCLInterface(1000, field)

#TODO something in pathfinder causes the program to not respond
# pathfinder = pathfinder.PathfinderInterface(field)
pathfinding_target = [500, 500]

# init odometry
past_odometry_data = [robot_pos_x, robot_pos_y, robot_angle]
curr_odometry_data = np.copy(past_odometry_data)

# Game loop
while running: 
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_q]: # Press 'q' to stop program
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN: # change target for pathfinding
            pathfinding_target = event.pos
    
    # make screen blank           
    screen.fill(SCREEN_COLOR)
    
    # update robot position
    d_x = 0
    d_y = 0
    d_theta = 0
    if keys[pygame.K_w]:
        d_y += 200 * dt * math.sin(robot_angle)
        d_x += 200 * dt * math.cos(robot_angle)
    if keys[pygame.K_s]:
        d_y -= 200 * dt * math.sin(robot_angle)
        d_x -= 200 * dt * math.cos(robot_angle)
    if keys[pygame.K_a]:
        d_x += 200 * dt * math.sin(robot_angle)
        d_y -= 200 * dt * math.cos(robot_angle) 
    if keys[pygame.K_d]:
        d_x -= 200 * dt * math.sin(robot_angle)
        d_y += 200 * dt * math.cos(robot_angle)
    if keys[pygame.K_j]:
        d_theta -= (math.pi) * 1.2 * dt
    if keys[pygame.K_k]:
        d_theta += (math.pi) * 1.2 * dt
    robot_pos.x += d_x
    robot_pos.y += d_y
    robot_angle += d_theta
    
    # update current odometry data 
    rand = np.random.default_rng()
    odometry_noise = rand.normal(np.zeros(3), 0.05*np.abs(np.array([d_x, d_y, d_theta]))) 
    curr_odometry_data += np.array([d_x, d_y, d_theta]) + odometry_noise
    
    # draw robot
    pygame.draw.circle(screen, "red", robot_pos, robot_radius)
    robot_orientation_x = robot_pos.x + robot_radius * math.cos(robot_angle)
    robot_orientation_y = robot_pos.y + robot_radius * math.sin(robot_angle)
    pygame.draw.line(screen, "purple", robot_pos, pygame.Vector2(robot_orientation_x, robot_orientation_y), 5)
    
    map.draw_map(screen, "blue", field, 3)
    
    # acquire LiDAR measurements and odometry data
    control = np.stack((past_odometry_data, curr_odometry_data))
    lidar.state = np.array([robot_pos.x, robot_pos.y, robot_angle])
    measurement, angles = lidar.measurements
    
    lidar.draw_measurements(screen, "yellow", 2)
    
    #TODO map not being fully enclosed causes errors, need to test with proper map
    #     might be able to fix this by also passing the angles of the rays to .update
    # robot location estimation
    # particles.update(control, measurement)
    # particles.draw_particles(screen, "red", 2)
    # particles.draw_state_estimation(screen, "green", robot_radius / 2)
    
    # path finding
    # pathfinder.find_path(particles.get_location()[:2], pathfinding_target)
    # pathfinder.draw_path(screen, 'white', 2)
    
    # update past odometry data
    past_odometry_data = np.copy(curr_odometry_data)

    # update display with the new drawings
    pygame.display.flip()
    
    # limits FPS to MAX_FPS
    # dt is delta time in seconds since last frame
    # Used for framerate independent physics
    dt = clock.tick(MAX_FPS) / 1000    
    
    print(f'fps: {clock.get_fps()}')
           
pygame.quit()

