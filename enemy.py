from abc import ABC, abstractmethod
import config
import player
from screen_object import ScreenObject
from world import World
from wall import Wall
from bullet import Bullet
import random, math, pygame, geometry
from player import Player

class Enemy(ScreenObject):
    def __init__(self, world: World, wall: Wall):        
        self.wall = wall
        self.size = config.ENEMY_SIZE

        if self.wall.orientation == 'vertical':
            world_x = self.wall.world_x - (self.wall.width / 2 + self.size / 2)
            world_y = random.randint(math.floor(self.wall.world_y), math.floor(self.wall.world_y + self.wall.height))
        else:
            world_x = random.randint(math.floor(self.wall.world_x), math.floor(self.wall.world_x + self.wall.width))
            world_y = self.wall.world_y - (self.wall.height / 2 + self.size / 2)

        super().__init__(world, world_x, world_y, self.size, self.size)

        self.speed = config.ENEMY_SPEED
        self.torch_radius = config.TORCH_RADIUS
        self.texture_size = config.ENEMY_TEXTURE_SIZE
        self.shoot_delay = 0
        self.bullets: list[Bullet] = []
        self.bullet_sound = pygame.mixer.Sound(config.BULLET_SOUND)

        enemy_surface = pygame.image.load(config.ENEMY_TEXTURE).convert_alpha()
        self.surface = pygame.transform.scale(enemy_surface, (self.texture_size, self.texture_size))

        self.direction = 1

    def can_see_player(self):
        player: Player | None = self._world.player
        walls: list[Wall] = self._world.walls

        if not player or self._world.is_game_over():
            return False

        # Check if player is in line of sight
        dx = player.world_x - self.world_x
        dy = player.world_y - self.world_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > self.torch_radius:
            return False

        # Check if any walls block the line of sight
        for wall in walls:
            left, top = wall.get_left_top_corner()

            # Line-rectangle intersection check
            if geometry.line_intersects_rect(self.world_x, self.world_y, player.world_x, player.world_y, 
                                       left, top, 
                                       wall.width, wall.height):
                return False
        return True

    def move(self):
        if self.can_see_player():
            return

        dy = 0
        dx = 0

        if self.wall.orientation == 'vertical':
            # Move up and down along vertical walls
            dy = self.speed * self.direction
        else:
            # Move left and right along horizontal walls
            dx = self.speed * self.direction

        # Check collisions with adjusted wall positions
        collision = False
        collision_rect = self.get_collision_rect(dx, dy)
        walls: list[Wall] = self._world.walls
        for wall in walls:
            collision = wall.check_collision(*collision_rect)
            if collision:
                break
        
        if not collision:
            enemies: list[Enemy] = self._world.enemies
            for enemy in enemies:
                if enemy == self:
                    continue

                collision = enemy.check_collision(*collision_rect)
                if collision:
                    break

        if collision:
            self.direction *= -1
        else:
            self.world_y += dy
            self.world_x += dx

        if self.wall.orientation == 'vertical':
            if self.world_y < self.wall.world_y or self.world_y - self.wall.world_y > self.wall.height:  # Patrol range
                self.direction *= -1
        else:
            if self.world_x < self.wall.world_x or self.world_x - self.wall.world_x > self.wall.width:  # Patrol range
                self.direction *= -1

    def _get_texture_rotation(self):
        player: Player | None = self._world.player

        if player and self.can_see_player():
            return 270 - math.degrees(math.atan2(self.world_y - player.world_y, self.world_x - player.world_x))

        if self.wall.orientation == 'vertical':
            return 90 - 90 * self.direction
        else:
            return 90 * self.direction

    def update(self):
        player: Player | None = self._world.player

        self.move()
        
        # Update existing bullets
        for bullet in self.bullets[:]:
            bullet.move()
            if not bullet.active:
                self.bullets.remove(bullet)
            # Check if any enemy bullets hit the player
            if bullet.check_hits_player() and player and player.invulnerable_timer <= 0:
                player.take_damage()
                bullet.active = False
                if player and player.lives <= 0:
                    self._world.end_game()                    

        # Shooting logic
        if self.shoot_delay > 0:
            self.shoot_delay -= 1
        elif player and self.can_see_player():
            angle = self._get_texture_rotation()
            texture_x, texture_y = config.ENEMY_GUN_END
            texture_x = texture_x - self.texture_size / 2
            texture_y = texture_y - self.texture_size / 2
            bullet_start_x, bullet_start_y = geometry.rotate_point(texture_x, texture_y, angle)
            self.bullets.append(Bullet(self._world, self.world_x + bullet_start_x, self.world_y + bullet_start_y, player.world_x, player.world_y))
            self.shoot_delay = config.ENEMY_SHOOT_DELAY * config.FRAMERATE
            self.bullet_sound.play()

    def draw(self, screen: pygame.Surface):
        player: Player | None = self._world.player

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
            
        # Draw enemy
        screen_x, screen_y = self.get_screen_coordinates()
        texture_x, texture_y = config.ENEMY_TEXTURE_CENTER
        texture_x = texture_x - self.texture_size / 2
        texture_y = texture_y - self.texture_size / 2
        angle = self._get_texture_rotation()
        rotated_x, rotated_y = geometry.rotate_point(texture_x, texture_y, angle)
        distance = math.sqrt((self.world_x - player.world_x)**2 + (self.world_y - player.world_y)**2) if player else 0
        if distance <= self.torch_radius and not self._world.is_game_over():
            enemy_surface = pygame.transform.rotate(self.surface, angle)
            rotated_rect = enemy_surface.get_rect(
                center=(screen_x - rotated_x, screen_y - rotated_y)
            )
            
            screen.blit(enemy_surface, rotated_rect.topleft)

        if config.DEBUG:
            pygame.draw.circle(screen, (0, 255, 0), (screen_x, screen_y), 2)
            pygame.draw.rect(screen, (0, 255, 0), self.get_screen_collision_rect(), 1)
