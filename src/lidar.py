import math
import pygame
import numpy as np
import src.map as map
import src.raycast as raycast
#TODO make lidar subclass of robot
class Lidar:
    
    def __init__(self, init_state, map: map.Map, angular_resolution: float, noise: float=0.1):
        self.state = init_state
        self.map = map
        self.angular_resolution = angular_resolution
        self.num_rays = int(2 * math.pi / math.radians(angular_resolution))
        self.noise = noise
        self.rand = np.random.default_rng()
        self._measurements = None
    
    @property
    def measurements(self):
        rays = raycast.compute_rays(self.num_rays, self.state[:2], self.state[2], self.map)
        diff = rays - self.state[0:2]
        r_distances = np.sqrt(np.sum(diff ** 2, axis=-1))
        # add noise
        new_r_distances = r_distances + self.rand.normal(scale=self.noise, size=(r_distances.size,))
    
        return new_r_distances
    
    # TODO fix this function
    def draw_measurements(self, surface: pygame.Surface, color: pygame.Color | str | tuple[int, int, int] | list[int], radius: int):
        measurements = self.measurements
        angles = np.linspace(0, 2 * math.pi, self.num_rays, endpoint=False) + self.state[2]
        x = self.state[0] + np.cos(angles) * measurements
        y = self.state[1] + np.sin(angles) * measurements
        measurement_endpts = np.stack((x, y), axis=-1)
        
        for measurement_endpt in measurement_endpts:
            pygame.draw.circle(surface, color, pygame.Vector2(*measurement_endpt), radius)
