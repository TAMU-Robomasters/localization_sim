import math
import numpy as np
import pygame
import src.map as map


def draw_rays(surface: pygame.surface, color: pygame.Color, center, rays, width: int):
    for ray in rays:
        pygame.draw.line(surface, color, center, [ray[0], ray[1]], width)
    

def compute_rays(num_rays: int, center, angle, map: map.Map):
    #TODO figure out best way to actually insert in numpy arrary
    rays = np.empty((1, 2))
    total_walls = np.concat([np.concat((boundary[:-1], boundary[1:]), axis=1) for boundary in map.boundaries]) 
    for ray_angle in np.linspace(0, 2 * math.pi, num_rays, endpoint=False) + angle:
        ray = np.array([center[0], center[1], center[0] + math.cos(ray_angle), center[1] + math.sin(ray_angle)])
        ra_degree = math.degrees(ray_angle)
             
        ray = _cast_ray(ray, total_walls)
        if ray.any():
            rays = np.append(rays, ray.reshape((1,2)), axis=0)
    
    return rays[1:]


def _cast_ray(ray, walls):
    
    # x1, y1 = walls[0][0], walls[0][1]
    # x2, y2 = walls[1][0], walls[1][1] 
    
    # x3, y3 = start[0], start[1]
    # x4, y4 = x3 + math.cos(angle), y3 + math.sin(angle) 
    denominator = (walls[:, 0] - walls[:, 2]) * (ray[1] - ray[3]) \
                - (walls[:, 1] - walls[:, 3]) * (ray[0] - ray[2])
    d_mask = denominator != 0
    # den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    # if den == 0:
    #     return -1 # did not collide into wall
    
    # t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    # u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
    
    t = ((walls[d_mask, 0] - ray[0]) * (ray[1] - ray[3]) \
      - (walls[d_mask, 1] - ray[1]) * (ray[0] - ray[2])) / denominator[d_mask]
    
    u = -((walls[d_mask, 0] - walls[d_mask, 2]) * (walls[d_mask, 1] - ray[1]) \
      -   (walls[d_mask, 1] - walls[d_mask, 3]) * (walls[d_mask, 0] - ray[0])) / denominator[d_mask]
    
    t_u_mask = (t > 0) & (t < 1) & (u > 0)
    walls = walls[d_mask][t_u_mask]
    
    t = t[t_u_mask]
    u = u[t_u_mask]
    # if t > 0 and t < 1 and u > 0:
    #     return [x1 + t * (x2 - x1), y1 + t * (y2 - y1)]
    
    colliding_rays_endpt = np.stack((
        walls[:, 0] + t * (walls[:, 2] - walls[:, 0]), 
        walls[:, 1] + t * (walls[:, 3] - walls[:, 1])
        ),
        axis=-1
    )
    if colliding_rays_endpt.any() == np.False_: # no colliding rays
        return np.empty(0)
    
    # find index with shortest length colliding ray
    colliding_ray_lengths = np.sqrt((ray[0] - colliding_rays_endpt[:, 0]) ** 2 + (ray[1] - colliding_rays_endpt[:, 1]) ** 2)
    ray_index = np.argmin(colliding_ray_lengths)

    return colliding_rays_endpt[ray_index]
    

    
    