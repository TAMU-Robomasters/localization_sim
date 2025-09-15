import cv2
import numpy as np
import pygame
from dataclasses import dataclass

@dataclass
class Map:
    name: str
    boundaries: list # list of numpy arrays
    starting_rect: np.ndarray # x_min, x_max, y_min, y_max
    outer_rect: np.ndarray # x_min, width, y_min, height
   

def load_map(surface: pygame.Surface, file_name: str) -> Map:
    map = Map
    map.name = file_name.rstrip('.jpeng')[5:] # skips 'maps/' rm extension
    map_img = cv2.imread(file_name)
    map_img_size = map_img.shape[:2] # pyright: ignore[reportOptionalMemberAccess]
    # find starting_rect if there is one
    hsv = cv2.cvtColor(map_img, cv2.COLOR_BGR2HSV) # pyright: ignore[reportCallIssue, reportArgumentType]
    red_lower_1 = (170, 100, 100)
    red_upper_1 = (180, 255, 255)
    red_lower_2 = (0, 100, 100)
    red_upper_2 = (15, 255, 255)
    red_mask_1 = cv2.inRange(hsv, red_lower_1, red_upper_1) # pyright: ignore[reportCallIssue, reportArgumentType]
    red_mask_2 = cv2.inRange(hsv, red_lower_2, red_upper_2) # pyright: ignore[reportCallIssue, reportArgumentType]
    
    red_mask = cv2.bitwise_or(red_mask_1, red_mask_2)
    
    red_contours, hiearchy = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(red_contours) != 0:
        red_contours = red_contours[0]
        # find rectangle estimation of drawing
        x, y, w, h = cv2.boundingRect(red_contours)
        map.starting_rect = np.array([x, x+w, y, y+h], dtype=np.float32)

    
    # find boundaries on the map
    gray = cv2.cvtColor(map_img, cv2.COLOR_BGR2GRAY) # pyright: ignore[reportCallIssue, reportArgumentType]
    ret, thresh = cv2.threshold(gray, 127, 255, 0)
    thresh = cv2.bitwise_not(thresh)
    thresh = cv2.bitwise_and(thresh, cv2.bitwise_not(red_mask)) # filter out starting rect
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    hierarchy = hierarchy[0]
    
    # determine how to resize map
    surface_ratio = surface.get_height() / float(surface.get_width())
    map_ratio = map_img_size[0] / float(map_img_size[1])
    if map_ratio >= surface_ratio:
        resize_factor = surface.get_height() / float(map_img_size[0])
    else:
        resize_factor = surface.get_width() / float(map_img_size[1])
    
    # compress and resize map to fit the screen
    map.boundaries = [] # inhomogenous array
    compressed_contours = []
    for i in range(len(hierarchy)):
        if hierarchy[i][3] == -1:
            epsilon = 0.0007 * cv2.arcLength(contours[i], True)
            compressed_contour = cv2.approxPolyDP(contours[i], epsilon, True)
            compressed_contours.append(compressed_contour)
            # makes iterating through map easier
            reformatted_contour = np.squeeze(np.concatenate((compressed_contour, compressed_contour[0:1])))
            resized_contour = reformatted_contour.astype(dtype=np.float32) * resize_factor
            map.boundaries.append(resized_contour)    
    map.starting_rect *= resize_factor
    x, y, w, h = cv2.boundingRect(compressed_contours[-1])
    map.outer_rect = np.array([x, w, y, h], dtype=np.float32) * resize_factor
    
    return map # pyright: ignore[reportReturnType]


def draw_map(surface: pygame.Surface, color: pygame.Color | str | tuple[int, int, int] | list[int], map: Map, width: int):  
    for boundary in map.boundaries:
        for i in range(len(boundary) - 1):
            pygame.draw.line(surface, color, pygame.Vector2(*boundary[i]), pygame.Vector2(*boundary[i + 1]), width)
