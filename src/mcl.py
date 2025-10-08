"""Implementation of Monte Carlo Localization (MCL) Algorithm"""
#TODO: Add docstrings for all classes and funcs

import math
import numpy as np
import pygame
import src.map as map
from localization_python.mcl import MCLImpl

class MCLInterface:
    
    def __init__(self, num_particles: int, map: map.Map):
        #TODO: decide if I should rename the keys in map
        map_bounds = {"x": map.outer_rect["x_min"], "y": map.outer_rect["y_min"], "w": map.outer_rect["width"], "h": map.outer_rect["height"]}
        starting_area = {"x": map.starting_rect["x_min"], "y": map.starting_rect["y_min"], "w": map.starting_rect["width"], "h": map.starting_rect["height"]}
        self.mcl = MCLImpl(num_particles=1000, walls=map.boundaries, map_bounds=map_bounds, starting_area=starting_area)   
         
    def update(self, control, measurement):
        self.mcl.update(control, measurement)
    
    def draw_state_estimation(self, surface: pygame.Surface, color: pygame.Color | str | tuple[int, int, int] | list[int], radius: int):
        state_estimation = self.mcl.get_estimated_location()
        
        position = [state_estimation[0], state_estimation[1]]
        pygame.draw.circle(surface, color, position, radius)
        # draw player's orientation
        particle_head_x = position[0] + radius * math.cos(state_estimation[2])
        particle_head_y = position[1] + radius * math.sin(state_estimation[2])
        pygame.draw.line(surface, "purple", position, pygame.Vector2(particle_head_x, particle_head_y), 5) 
        
    def draw_particles(self, surface: pygame.Surface, color: pygame.Color | str | tuple[int, int, int] | list[int], max_radius: int):
        particles = self.mcl.get_particles()
        
        for state, weight in zip(particles['states']):
            if weight <= 0:
                continue
            radius = int(3)
            p_pos = (float(state[0]), float(state[1]))
            try:
                pygame.draw.circle(surface=surface, color=color, center=p_pos, radius=radius)
            except TypeError as e:
                print(f"p_pos: {p_pos} of type {type(p_pos)} with {[type(a) for a in p_pos]}")
                raise e
            # draw player's orientation
            particle_head_x = state[0] + radius * math.cos(state[2])
            particle_head_y = state[1] + radius * math.sin(state[2])
            pygame.draw.line(surface, "purple", p_pos, pygame.Vector2(particle_head_x, particle_head_y), radius // 2)
            