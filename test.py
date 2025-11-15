import numpy as np
import math
import os
import time
from dotenv import load_dotenv
from src import map, mcl, lidar

load_dotenv()

screen = ""

field = map.load_map(screen, os.path.join("maps/",str(os.getenv("MAP"))))
robot_pos_x = (2 * field.starting_rect['x_min'] + field.starting_rect['width']) / 2
robot_pos_y = (2 * field.starting_rect['y_min'] + field.starting_rect['height']) / 2
robot_angle = math.radians(-90)

lidar = lidar.Lidar(np.array([robot_pos_x, robot_pos_y, robot_angle]), field, 3, 4)

particles = mcl.MCLInterface(1000, field)


while True:
    start_time = time.perf_counter_ns()
    # update current data 
    past_odometry_data = np.array([1, 1, 1])
    curr_odometry_data = past_odometry_data + 0.1
    control = np.stack((past_odometry_data, curr_odometry_data))
    lidar.state = np.array([robot_pos_x, robot_pos_y, robot_angle])
    measurement, angles = lidar.measurements

    # get estimate
    particles.update(control, measurement)
    location = particles.get_location()
    
    print(f'fps: {1E9 / float(time.perf_counter_ns() - start_time)}')


