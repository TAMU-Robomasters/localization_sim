import math
import numpy as np
import pygame
import src.map as map


def draw_rays(surface: pygame.surface, color: pygame.Color, center, rays, width: int):
    for ray in rays:
        pygame.draw.line(surface, color, center, [ray[0], ray[1]], width)
    

def compute_rays(num_rays: int, center, angle, map: map.Map):
    """ Performs ray casting algorithm

    Args:
        num_rays (int): Ray's are evenly spaced between 0 and 2pi
        center (2x1 array): the origin of all the rays
        angle (float): the angular offset of all the rays 
        map (map.Map): A list of closed contours that describe the layout of the map

    Returns:
        nx2x1 numpy array: the coordinates of where all the rays collided
    """
    #TODO figure out best way to actually insert in numpy arrary
    rays = np.empty((1, 2))
    angles = np.empty((1, 1))
    total_walls = np.concatenate([np.concatenate((boundary[:-1], boundary[1:]), axis=1) for boundary in map.boundaries]) 
    for ray_angle in np.linspace(0, 2 * math.pi, num_rays, endpoint=False) + angle:
        ray = np.array([center[0], center[1], center[0] + math.cos(ray_angle), center[1] + math.sin(ray_angle)])
        ra_degree = math.degrees(ray_angle)
             
        ray = _cast_ray(ray, total_walls)
        if ray.any():
            rays = np.append(rays, ray.reshape((1,2)), axis=0)
            angles = np.append(angles, ray_angle)

        # else:
        #     rays = np.append(rays, ray.reshape((1,2)), axis=0)


    
    return (rays[1:], angles[1:])


def _cast_ray(ray, walls):
    """Given the unit vector of a ray find where it collides against a wall.
    Algorithm basically checks every wall to see if the ray collided against it or not.
    
    Formula is from [Coding Challenge 145: 2D Raycasting](https://youtu.be/TOEi6T2mtHo?si=HrVhc1_BFAD5qMuc)
    and was numpy-ified so that it all runs in C

    Args:
        ray (4x1 numpy array): the first two elements are the origin of the ray (i.e. LiDAR location).
        The last two elements contain the x and y of the ray if it were to only go one unit in the rays
        direction. It basically the unit vector translated to the origin of the ray.
        
        walls (nx4x1 numpy array): a list of 4x1 numpy arrays that represent the different line segments
        that describe the map. The first two elements in the 4x1 numpy array represent 
        one of the endpt of the wall and the last two elements represent the other endpt of the wall. 
        The walls are listed in order so the second endpt of a wall should be the first endpt of the next wall 
        in the list.

    Returns:
        2x1 numpy array: The coordinate of where the ray collided. Will return empty array if ray
        never collides with anything.
    """
    
    denominator = (walls[:, 0] - walls[:, 2]) * (ray[1] - ray[3]) \
                - (walls[:, 1] - walls[:, 3]) * (ray[0] - ray[2])
    d_mask = denominator != 0
    
    t = ((walls[d_mask, 0] - ray[0]) * (ray[1] - ray[3]) \
      - (walls[d_mask, 1] - ray[1]) * (ray[0] - ray[2])) / denominator[d_mask]
    
    u = -((walls[d_mask, 0] - walls[d_mask, 2]) * (walls[d_mask, 1] - ray[1]) \
      -   (walls[d_mask, 1] - walls[d_mask, 3]) * (walls[d_mask, 0] - ray[0])) / denominator[d_mask]
    
    t_u_mask = (t > 0) & (t < 1) & (u > 0)
    walls = walls[d_mask][t_u_mask]
    
    t = t[t_u_mask]
    u = u[t_u_mask]
    
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
    

    
    