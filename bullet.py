from operator import is_
from screen_object import ScreenObject
from wall import Wall
from world import World
import math, pygame, config

class Bullet(ScreenObject):
    def __init__(self, world: World, world_x, world_y, target_world_x, target_world_y, color=(255, 0, 0), is_enemy=True):
        super().__init__(world, world_x, world_y, config.BULLET_SIZE, config.BULLET_SIZE)
        self.target_world_x = target_world_x
        self.target_world_y = target_world_y
        self.color = color
        self.is_enemy = is_enemy
        self.speed = config.ENEMY_BULLET_SPEED if is_enemy else config.PLAYER_BULLET_SPEED
        
        # Calculate direction vector
        dx = target_world_x - world_x
        dy = target_world_y - world_y
        length = math.sqrt(dx * dx + dy * dy)
        # Store normalized direction vector
        self.dx = dx / length if length > 0 else 0
        self.dy = dy / length if length > 0 else 0
        self.size = config.BULLET_SIZE
        self.active = True

    def move(self):
        # Calculate actual movement based on speed and delta time
        move_x = self.dx * self.speed * self._world.dt
        move_y = self.dy * self.speed * self._world.dt

        # Check collisions with adjusted wall positions
        collision = False
        collision_rect = self.get_collision_rect(move_x, move_y)
        walls: list[Wall] = self._world.walls
        for wall in walls:
            collision = wall.check_collision(*collision_rect)
            if collision:
                break
        
        if collision:
            self.active = False
        else:
            self.world_x += move_x
            self.world_y += move_y

    def draw(self, screen: pygame.Surface):
        screen_x, screen_y = self.get_screen_coordinates()
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)
        
        if config.DEBUG:
            pygame.draw.rect(screen, (0, 255, 0), self.get_screen_collision_rect(), 1)

    def check_hits_player(self):
        if not self.is_enemy:
            return False
            
        player = self._world.player
        if not player:
            return False

        return player.check_collision(*self.get_collision_rect())

    def check_hits_enemies(self):
        if self.is_enemy:
            return []
            
        hits = []
        for enemy in self._world.enemies:
            if not enemy.dead and enemy.check_collision(*self.get_collision_rect()):
                hits.append(enemy)
        return hits
