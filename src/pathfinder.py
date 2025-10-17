"""Uses c++ extension to compute correct path"""
import pathfinding_python as pfp
import src.map as map
import numpy as np
import pygame
from typing import List


class PathfinderInterface:
    def __init__(self, map: map.Map) -> None:
        # last boundary is the outer wall
        self._vg = self._load_map(map.boundaries[:-1])
        self._path = []
        
    def _load_map(self, inner_boundaries: List[np.ndarray]) -> pfp.VizGraph:
        polygons = []
        for inner_boundary in inner_boundaries:
            polygon = [pfp.Point(point[0], point[1]) for point in inner_boundary]
            polygons.append(polygon)
        
        return pfp.constructVizGraph(polygons, [])
    
    def find_path(self, start: List[float], end: List[float]) -> None:
        path = self._vg.search(start[0], start[1], end[0], end[1])
        path = np.array([[point.x, point.y] for point in path])
        self._path = path
    
    def draw_path(self, surface: pygame.Surface, color: pygame.Color | str | tuple[int, int, int] | list[int], width: int) -> None:
        # draw path
        for i in range(len(self._path) - 1):
            pygame.draw.line(surface, color, pygame.Vector2(*self._path[i]), pygame.Vector2(*self._path[i + 1]), width)
        
        # draw target position
        if len(self._path) > 0:
            pygame.draw.circle(surface, 'red', center=(self._path[-1]), radius=width*2)