"""Implementation of Monte Carlo Localization (MCL) Algorithm"""
import math
import numpy as np
import pygame
import os
import src.map as map

import cv2

class Particles:
    
    def __init__(self, num_particles, map:map.Map, surface:pygame.Surface):
        self.rand = np.random.default_rng()
        self.num_particles = num_particles
        bounds = map.starting_rect
        p_x = self.rand.uniform(bounds[0], bounds[1], (num_particles, 1))
        p_y = self.rand.uniform(bounds[2], bounds[3], (num_particles, 1))
        p_theta = self.rand.uniform(0, 2 * math.pi, (num_particles, 1))
        self.states = np.concatenate((p_x, p_y, p_theta), axis=-1)
        self.weights = np.full((num_particles, 1), 1 / num_particles)
        self.particle_radius = 10
        self._state_estimation = None
        self.map = map
        self.arr_size = None
        self.offset = None
        self.resamp_factor = None
        self.distances = self.load_pre_compute(surface, map, resamp_factor=2)
        
    
    @property
    def state_estimation(self):
        return np.sum(self.states * self.weights, axis=0)

    def draw_state_estimation(self, surface: pygame.Surface, color: pygame.Color):
        pos = [self.state_estimation[0], self.state_estimation[1]]
        pygame.draw.circle(surface, color, pos, self.particle_radius)
        # draw player's orientation
        particle_head_x = pos[0] + self.particle_radius * math.cos(self.state_estimation[2])
        particle_head_y = pos[1] + self.particle_radius * math.sin(self.state_estimation[2])
        pygame.draw.line(surface, "purple", pos, pygame.Vector2(particle_head_x, particle_head_y), 5) 
        
    def draw_particles(self, surface: pygame.Surface, color: pygame.Color, max_radius: int):
        for state, weight in zip(self.states, np.log10(self.weights * 2000).squeeze()):
            if weight <= 0:
                continue
            radius = int(max_radius * weight)
            p_pos = [state[0], state[1]]
            pygame.draw.circle(surface, color, p_pos, radius)
            # draw player's orientation
            particle_head_x = state[0] + radius * math.cos(state[2])
            particle_head_y = state[1] + radius * math.sin(state[2])
            pygame.draw.line(surface, "purple", p_pos, pygame.Vector2(particle_head_x, particle_head_y), radius // 2)
    
    def find_min_dist(self, px , py, walls):
        point = np.array([px, py])
        v = walls[:, :2]
        w = walls[:, 2:]
        diff = w - v
        
        # project point against all walls, 
        length_squared = np.vecdot(diff, diff)
        # t should limited to [0,1]
        t = np.expand_dims(np.max(np.expand_dims(np.min(np.expand_dims(np.vecdot(point - v, diff) / length_squared, axis=-1), axis=-1, initial=1), axis=-1), axis=-1, initial=0), axis=-1)
        # projection is the closest point on the wall to the point param
        projections = v + t * (w - v)
        
        distances = np.sqrt(np.sum((point - projections) ** 2, axis=-1))
        return np.min(distances)
        
    # TODO verify that this actually works fully and figure shape stuff so that it covers
    # TODO the entire map 
    def load_pre_compute(self, surface: pygame.Surface, map:map.Map, resamp_factor: float):
        #TODO deal with the fact that the x or y might not be a negative number 
        #TODO deal with the fact that the height might be bigger than the width
        o_r = map.outer_rect
        expanded_map = np.array([o_r[0] - o_r[1], o_r[1] * 3, o_r[2] - o_r[1], o_r[1] * 2 + o_r[3]])
        expanded_map_size = (3 * o_r[1], 2 * o_r[1] + o_r[3])
        
        size_0 = expanded_map_size[0] / resamp_factor
        size_1 = expanded_map_size[1] / resamp_factor
        arr_size = (int(size_0), int(size_1))
        offset = (expanded_map[0], expanded_map[2])
        self.arr_size = arr_size
        self.offset = offset
        self.resamp_factor = resamp_factor
        file_name = map.name + f'_{resamp_factor}' + '.npy' 
        if file_name in os.listdir('src/mcl_pre_compute'):
            return np.load('src/mcl_pre_compute/' + file_name)
        
        # do pre compute, store it in a file, and return pre compute as contiguous array for O(1) element access
        total_walls = np.concatenate([np.concatenate((boundary[:-1], boundary[1:]), axis=1) for boundary in self.map.boundaries])
        distances = np.empty((arr_size[0], arr_size[1]), dtype=np.float32)
        # projections = np.empty((size[0], size[1], 2), dtype=np.float32)
        # shape = projections.shape
        for i in range(arr_size[0]):
            for j in range(arr_size[1]):
                distance = self.find_min_dist(i * resamp_factor + offset[0] , j * resamp_factor + offset[1], total_walls)
                distances[i, j] = distance
                # projection = self.find_min_dist(i * x_factor, j * y_factor, total_walls)
                # projections[i, j] = projection
        file_name = 'src/mcl_pre_compute/' + map.name + f'_{resamp_factor}' + '.npy'
        
        np.save(file_name, distances)
        return distances
        # np.save(file_name, projections)
        # return projections
    
    def draw_projections(self, surface: pygame.Surface, color: pygame.Color, projections: np.ndarray, width: int):
        shape = projections.shape
        x_factor = surface.get_width() / shape[0]
        y_factor = surface.get_height() / shape[1]
        for i in range(shape[0]):
            for j in range(shape[1]):
                pygame.draw.circle(surface, color, [i * x_factor, j * y_factor], 5)
                pygame.draw.line(surface, color, [i * x_factor, j * y_factor], list(projections[i, j]), width)
    
    def update_particles(self, control, measurement, surface: pygame.Surface, map:map.Map, a1=0.01, a2=0.01, a3=0.01, a4=0.01):
        """Uses Monte Carlo Localization to update particle states and weights"""
        
        # motion model
        del_rot1 = np.arctan2(control[1][1] - control[0][1], control[1][0] - control[0][0]) \
             - control[0][2]
        diff = np.diff(control[:, :2], axis=0)
        del_trans = np.sqrt(np.sum(diff ** 2, axis=-1))
        del_rot2 = control[1][2] - control[0][2] - del_rot1
        
        # carrot rot1
        c_r1 = del_rot1 \
             - self.rand.normal(scale=np.sqrt(a1 * del_rot1 ** 2 + a2 * del_trans ** 2), size=(self.num_particles,))
        c_t = del_trans \
            - self.rand.normal(scale=np.sqrt(a3 * del_trans ** 2 + a4 * del_rot1 ** 2 + a4 * del_rot2 ** 2), size=(self.num_particles,))
        c_r2 = del_rot2 \
             - self.rand.normal(scale=np.sqrt(a1 * del_rot2 ** 2 + a2 * del_trans ** 2), size=(self.num_particles,))
             
        x_prime = self.states[:, 0] + c_t * np.cos(self.states[:, 2] + c_r1)
        y_prime = self.states[:, 1] + c_t * np.sin(self.states[:, 2] + c_r1)
        theta_prime = self.states[:, 2] + c_r1 + c_r2
        
        # update all particle's state based on motion model
        self.states = np.stack((x_prime, y_prime, theta_prime), axis=-1)
        # !TODO decide how to deal with edge case where not all of the rays hit anything
        # !!!^
        # update all particle's weights based on measurement model
        # 1. find the endpts of the measurements given the state of each particle and actual measurement
        
        particle_angles = np.linspace(0, 2 * math.pi, measurement.size, endpoint=False)
        particle_angles = np.broadcast_to(particle_angles, (self.num_particles, measurement.size)) + self.states[:, 2].reshape((self.num_particles, 1))
        measurement = measurement
        x = self.states[:, 0]
        x = x.reshape((x.size, 1))
        y = self.states[:, 1]
        y = y.reshape((y.size, 1))
        x_z = x + np.cos(particle_angles) * measurement
        y_z = y + np.sin(particle_angles) * measurement
        # 2. find the distance from each endpt to the respective nearest wall
        # use pre computed data for O(1) calculation
        x_indices = ((x_z - self.offset[0]) / self.resamp_factor).astype(int)
        y_indices = ((y_z - self.offset[1]) / self.resamp_factor).astype(int)
        print(x_indices.shape, y_indices.shape)
        print(self.distances.shape)
        print(self.offset)
        distances = self.distances[x_indices, y_indices]
        print(distances)
        print(distances.shape)
        
        #TODO create a simulated particle to make sure everything is working
        
        std_dev = 50
        z_hit = 1E3
        probabilities = (1 / math.sqrt(2 * math.pi * (std_dev ** 2))) * np.exp(-0.5 * (distances ** 2) / (std_dev ** 2)) * z_hit
        print(probabilities)
        print(probabilities.dtype)
        q = np.prod(probabilities, axis=-1, keepdims=True)
        print(q.dtype)
        print(q[:10])
        print(np.sum(q))
        # update particle weights
        weights = q / np.sum(q) 
        self.weights = weights
        
        # resample and create new particle set
        new_states = np.empty((1000,3), dtype=np.float32)
        r = self.rand.uniform(0, 1 / self.num_particles)
        curr_sum = weights[0][0]
        i = 0
        for j in range(self.num_particles):
            U = r + j * 1 / self.num_particles
            while U > curr_sum:
                i += 1
                curr_sum += weights[i][0]
                print(f"current sum: {curr_sum}")
            new_states[j] = self.states[i]
            
        self.states = new_states
        self.weights = np.full((self.num_particles, 1), 1 / self.num_particles)

    