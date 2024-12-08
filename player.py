import pygame, math, random, config, geometry
from world import World
from screen_object import ScreenObject
from bullet import Bullet
from bonus import Bonus

class Player(ScreenObject):
    def __init__(self, world: World, world_x: float, world_y: float):
        super().__init__(world, world_x, world_y, config.PLAYER_SIZE, config.PLAYER_SIZE)

        self.torch_surface = None
        self.torch_radius = config.TORCH_RADIUS
        self.texture_size = config.PLAYER_TEXTURE_SIZE
        self.player_size = config.PLAYER_TEXTURE_SIZE
        self.lives = config.PLAYER_LIVES
        self.invulnerable_timer = 0
        self.rotation = 0  # Current rotation angle in degrees
        self.rotation_speed = config.PLAYER_ROTATION_SPEED
        self.bullets = []
        self.bullets_left = config.PLAYER_MAX_BULLETS

        self.shoot_delay = 0
        self.recharge_timer = 0
        self.night_vision_timer = 0

        self.bullet_sound = pygame.mixer.Sound(config.BULLET_SOUND)
        self.recharge_sound = pygame.mixer.Sound(config.PLAYER_BULLET_RECHARGE_SOUND)
        self.recharge_sound.set_volume(0.5)
        self.player_hurt_sound = pygame.mixer.Sound(config.PLAYER_HURT_SOUND)

        self.debug = {}

        try:
            self.surface = pygame.image.load(config.PLAYER_TEXTURE).convert_alpha()
            self.surface = pygame.transform.scale(self.surface, (self.texture_size, self.texture_size))
        except pygame.error:
            print("Could not load player texture")
            self.surface = None

        # Create torch light surface
        self.torch_surface = pygame.Surface((self.torch_radius * 2, self.torch_radius * 2), pygame.SRCALPHA)
        for radius in range(self.torch_radius, 0, -1):
            alpha = int(255 * (1 - radius / self.torch_radius))
            color = (255, 255, 255, alpha)
            pygame.draw.circle(self.torch_surface, color, (self.torch_radius, self.torch_radius), int(radius))

    def shoot(self):
        if self.shoot_delay > 0 or self.bullets_left <= 0:
            return
            
        # Calculate target point based on player rotation
        rotation_rad = math.radians(self.rotation)
        
        # Get gun position
        texture_x, texture_y = config.PLAYER_GUN_END
        texture_x = texture_x - self.texture_size / 2
        texture_y = texture_y - self.texture_size / 2
        bullet_start_x, bullet_start_y = geometry.rotate_point(texture_x, texture_y, self.rotation)
        
        target_x = self.world_x + bullet_start_x + math.sin(rotation_rad) * 100
        target_y = self.world_y + bullet_start_y + math.cos(rotation_rad) * 100

        # Create bullet
        self.bullets.append(Bullet(self._world, 
                                 self.world_x + bullet_start_x, 
                                 self.world_y + bullet_start_y, 
                                 target_x, target_y, 
                                 color=config.PLAYER_BULLET_COLOR,
                                 is_enemy=False))
        self.shoot_delay = config.PLAYER_SHOOT_DELAY * config.FRAMERATE
        self.bullets_left -= 1
        
        # Play sound
        self.bullet_sound.play()

    def move(self, forward: float):
        # Convert rotation to radians for math calculations
        rotation_rad = math.radians(self.rotation)
        
        # Calculate movement vector based on rotation
        dx = math.sin(rotation_rad) * forward * config.PLAYER_SPEED
        dy = math.cos(rotation_rad) * forward * config.PLAYER_SPEED

        enemies = list(filter(lambda enemy: not enemy.dead, self._world.enemies))
        collidable_objects: list[ScreenObject] = [*self._world.walls, *enemies]

        # Check collisions with adjusted wall positions
        collision = False
        # Check dx and dy separately to allow for alternative movement
        collision_x = False
        collision_y = False
        collision_rect = self.get_collision_rect(dx, dy)
        x_collision_rect = self.get_collision_rect(dx, 0)
        y_collision_rect = self.get_collision_rect(0, dy)
        
        hits = []

        for collidable_object in collidable_objects:
            hit = { "id": collidable_object._id, "total": False, "x": False, "y": False }

            if collidable_object.check_collision(*collision_rect):
                collision = True
                hit['total'] = True
            
            if collidable_object.check_collision(*x_collision_rect):
                collision_x = True
                hit['x'] = True
            
            if collidable_object.check_collision(*y_collision_rect):
                collision_y = True
                hit['y'] = True

            if hit['total']:
                hits.append(hit)
        
        if collision: 
            if collision_x:
                dx = 0

            if collision_y:
                dy = 0

        if dx != 0 or dy != 0:
            self.world_x += dx
            self.world_y += dy
            self._world.offset(dx, dy)

        if config.DEBUG:
            self.debug['collision_hits'] = hits

    def rotate(self, angle_change: float):
        self.rotation = (self.rotation - angle_change * self.rotation_speed) % 360

    def get_texture_rotation(self):
        return self.rotation

    def take_damage(self):
        if self.invulnerable_timer <= 0:
            self.lives -= 1
            self.invulnerable_timer = config.PLAYER_INVULNERABILITY_TIME * config.FRAMERATE
            self.player_hurt_sound.play()

    def start_night_vision(self):
        self.night_vision_timer += config.GOOGLES_ACTIVE_TIME * config.FRAMERATE

    def heal(self, amount: int):
        self.lives = min(self.lives + amount, config.PLAYER_LIVES)

    def update(self):
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.move()
            if not bullet.active:
                self.bullets.remove(bullet)
                continue
                
            # Check if bullet hits any enemies
            hits = bullet.check_hits_enemies()
            if hits:
                bullet.active = False
                self.bullets.remove(bullet)
                # Remove hit enemies
                for enemy in hits:
                    if enemy in self._world.enemies:
                        enemy.take_damage()
                        # Chance to spawn aid kit
                        if random.random() < config.BONUS_SPAWN_CHANCE:
                            self._world.bonuses.append(Bonus(self._world, enemy.world_x, enemy.world_y))

        if self._world.is_game_over():
            return
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            
        if self.shoot_delay > 0:
            self.shoot_delay -= 1

        if self.night_vision_timer > 0:
            self.night_vision_timer -= 1

        # Recharge bullets
        if self.bullets_left < config.PLAYER_MAX_BULLETS:
            self.recharge_timer += 1
            if self.recharge_timer >= config.PLAYER_BULLET_RECHARGE_TIME * config.FRAMERATE:
                self.bullets_left += 1
                self.recharge_sound.play()
                self.recharge_timer = 0

    def draw(self, screen: pygame.Surface):
        if not self.surface:
            return
            
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
            
        screen_x, screen_y = self.get_screen_coordinates()
        texture_x, texture_y = config.PLAYER_TEXTURE_CENTER
        texture_x = texture_x - self.texture_size / 2
        texture_y = texture_y - self.texture_size / 2
        blink_factor = self.invulnerable_timer * 5 / config.FRAMERATE
        should_blink = blink_factor - math.floor(blink_factor) < 0.5

        if (self.invulnerable_timer <= 0 or should_blink) and not self._world.is_game_over():
            texture_x, texture_y = config.ENEMY_TEXTURE_CENTER
            texture_x = texture_x - self.texture_size / 2
            texture_y = texture_y - self.texture_size / 2
            rotated_x, rotated_y = geometry.rotate_point(texture_x, texture_y, self.rotation)
            player_surface = pygame.transform.rotate(self.surface, self.rotation)
            rotated_rect = player_surface.get_rect(
                center=(screen_x - rotated_x, screen_y - rotated_y)
            )
            screen.blit(player_surface, rotated_rect.topleft)
    
        # Create torch light effect
        light_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        light_surface.fill(config.COLOR_DARK)
        
        # Apply the main torch light
        if not self._world.is_game_over():
            if self.torch_surface != None and self.night_vision_timer <= 0:
                current_torch_radius = random.randint(config.TORCH_RADIUS - 5, config.TORCH_RADIUS + 5)
                scaled_torch = pygame.transform.scale(self.torch_surface, (current_torch_radius * 2, current_torch_radius * 2))
                light_surface.blit(scaled_torch, 
                        (int(screen_x - current_torch_radius), 
                        int(screen_y - current_torch_radius)), 
                        special_flags=pygame.BLEND_RGBA_SUB)

            if self.night_vision_timer > 0:
                light_surface.fill(config.COLOR_NIGHT_VISION)

            screen.blit(light_surface, (0, 0))

        if config.DEBUG:
            pygame.draw.circle(screen, (0, 255, 0), (screen_x, screen_y), 2)
            pygame.draw.rect(screen, (0, 255, 0), self.get_screen_collision_rect(), 1)
            font = pygame.font.Font(None, 18)
            if 'collision_hits' in self.debug:
                hits = self.debug['collision_hits']
                text = font.render(f"Collision debug: {hits}", True, (255, 255, 255))
                screen.blit(text, (4, config.SCREEN_HEIGHT - 20))
            
            text = font.render(f"Player position: {(round(self.world_x, 2), round(self.world_y, 2))}", True, (255, 255, 255))
            screen.blit(text, (4, config.SCREEN_HEIGHT - 40))
            