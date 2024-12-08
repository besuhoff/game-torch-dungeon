from abc import ABC, abstractmethod
from world import World
import pygame

class ScreenObject(ABC):
    _id: int = 0

    def __init__(self, world: World, world_x: float, world_y: float, width: float, height: float):
        self._world = world
        self.width = width
        self.height = height
        self.world_x = world_x
        self.world_y = world_y
        ScreenObject._id += 1
        self._id = ScreenObject._id

    def get_screen_coordinates(self):
        return self._world.world_to_screen_coordinates(self.world_x, self.world_y)

    def get_collision_rect(self, dx: float = 0, dy: float = 0) -> tuple[float, float, float, float]:
        return (self.world_x + dx - self.width / 2, self.world_y + dy - self.height / 2, self.width, self.height)

    def get_screen_collision_rect(self, dx: float = 0, dy: float = 0) -> tuple[float, float, float, float]:
        coll_x, coll_y, coll_w, coll_h = self.get_collision_rect()
        screen_coll_x, screen_coll_y = self._world.world_to_screen_coordinates(coll_x, coll_y)
        return (screen_coll_x, screen_coll_y, coll_w, coll_h)

    def check_collision(self, rect_world_x, rect_world_y, rect_width, rect_height):
        return pygame.Rect(*self.get_collision_rect()).colliderect(rect_world_x, rect_world_y, rect_width, rect_height)
