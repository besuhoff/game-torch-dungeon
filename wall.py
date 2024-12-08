from screen_object import ScreenObject
import pygame, config

from world import World

class Wall(ScreenObject):
    def __init__(self, world: World, world_x: float, world_y: float, width: float, height: float, orientation):
        super().__init__(world, world_x, world_y, width, height)

        self.width = width
        self.height = height
        self.orientation = orientation

        try:
            self.texture = pygame.image.load(config.WALL_TEXTURE)
            self.texture = pygame.transform.scale(self.texture, (self.width, self.height) if self.orientation == 'horizontal' else (self.height, self.width))
            if self.orientation == 'vertical':
                self.texture = pygame.transform.rotate(self.texture, 90)
        except pygame.error:
            print("Could not load wall texture. Using default color.")
            self.texture = None

    def get_collision_rect(self, dx: float = 0, dy: float = 0) -> tuple[float, float, float, float]:
        left, top = self.get_left_top_corner()
        return left + dx, top + dy, self.width, self.height

    def draw(self, screen: pygame.Surface):
        (left, top) = self.get_left_top_corner()
        x, y = self._world.world_to_screen_coordinates(left, top)

        # Create screen rect with world offset
        screen_rect = pygame.Rect(
            x,
            y,
            self.width,
            self.height
        )
        if self.texture:
            screen.blit(self.texture, screen_rect)

        if config.DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), self.get_screen_collision_rect(), 1)
            font = pygame.font.Font(None, 18)
            text = font.render(f"{self._id}", True, (255, 255, 255))
            screen.blit(text, (x + 2, y + 2))

    def get_left_top_corner(self):
        correction_w = 0
        correction_h = 0
        if self.orientation == 'vertical':
            correction_w = self.width / 2
        else:
            correction_h = self.height / 2

        return self.world_x - correction_w, self.world_y - correction_h
