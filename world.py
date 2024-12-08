from abc import ABC
import pygame, math, random, config

class World:
    _game_over = False
    CHUNK_SIZE = 800  # Size of each chunk

    def __init__(self, Player, Enemy, Wall, Bonus):
        self.offset_x = 0
        self.offset_y = 0
        self._Player = Player
        self._Enemy = Enemy
        self._Wall = Wall
        self._Bonus = Bonus
        self.walls = []
        self.enemies = []
        self.bonuses = []
        self.player = None
        self.dt = 0.0  # Time delta in seconds
        self.generated_chunks = set()  # Keep track of generated chunks
        self.torch_sound = pygame.mixer.Sound(config.TORCH_SOUND)
        self.game_over_sound = pygame.mixer.Sound(config.GAME_OVER_SOUND)

    def get_chunk_coords(self, x, y):
        # Convert world coordinates to chunk coordinates
        chunk_x = x // self.CHUNK_SIZE
        chunk_y = y // self.CHUNK_SIZE
        return chunk_x, chunk_y

    def generate_walls_for_chunk(self, chunk_x: float, chunk_y: float):        
        # If chunk already generated, skip
        if (chunk_x, chunk_y) in self.generated_chunks:
            return
        
        # Mark chunk as generated
        self.generated_chunks.add((chunk_x, chunk_y))
        
        # Calculate chunk boundaries
        chunk_start_x = chunk_x * self.CHUNK_SIZE
        chunk_start_y = chunk_y * self.CHUNK_SIZE
        
        # Generate 2-3 random walls in this chunk
        num_walls = random.randint(2, 3)
        new_walls = []
        
        for _ in range(num_walls):
            # Randomly decide wall orientation
            orientation = random.choice(['vertical', 'horizontal'])
            
            if orientation == 'vertical':
                wall_x = random.randint(math.floor(chunk_start_x + 100), math.floor(chunk_start_x + self.CHUNK_SIZE - 100))
                wall_y = random.randint(math.floor(chunk_start_y + 100), math.floor(chunk_start_y + self.CHUNK_SIZE - 200))
                width = 30
                height = random.randint(200, 300)
            else:
                wall_x = random.randint(math.floor(chunk_start_x + 100), math.floor(chunk_start_x + self.CHUNK_SIZE - 200))
                wall_y = random.randint(math.floor(chunk_start_y + 100), math.floor(chunk_start_y + self.CHUNK_SIZE - 100))
                width = random.randint(200, 300)
                height = 30
            
            new_walls.append((wall_x, wall_y, width, height, orientation))
        
        # Add new walls
        for wall_params in new_walls:
            wall = self._Wall(self, *wall_params)
            self.walls.append(wall)
            # Create enemy for each wall
            self.enemies.append(self._Enemy(self, wall))
    
    def update_chunks(self):
        if self.player:
            # Get current chunk coordinates
            current_chunk_x, current_chunk_y = self.get_chunk_coords(
                self.player.world_x, self.player.world_y
            )
            
            # Generate walls for current and adjacent chunks
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    self.generate_walls_for_chunk(current_chunk_x + dx, current_chunk_y + dy)
    
    def update(self):
        if self.player:
            self.player.update()
        
        self.update_chunks()

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            
        # Update aid kits
        for bonus in self.bonuses[:]:
            bonus.update()
                
    def world_to_screen_coordinates(self, x: float, y: float):
        return x + self.offset_x + config.SCREEN_WIDTH // 2, y + self.offset_y + config.SCREEN_HEIGHT // 2
        
    def offset(self, dx, dy):
        self.offset_x -= dx
        self.offset_y -= dy

    def create_player(self):
        self.player = self._Player(self, 0, 0)

    def create_walls(self, walls: list[tuple[int, int, int, int, str]]):
        self.walls = []
        for wall in walls:
            self.walls.append(self._Wall(self, *wall))

    def create_enemies(self):
        self.enemies = []
        for wall in self.walls:
            self.enemies.append(self._Enemy(self, wall))

    def end_game(self):
        self.torch_sound.stop()
        self._game_over = True
        self.game_over_sound.play()
    
    def start_game(self):
        self.walls = []
        self.enemies = []
        self.bonuses = []
        self.generated_chunks = set()
        self.create_player()
        self.update_chunks()  # Generate initial chunks
        self.offset_x = self.offset_y = 0
        self.torch_sound.play(-1)
        self._game_over = False
    
    def is_game_over(self):
        return self._game_over

    def draw(self, screen: pygame.Surface):
        # Draw walls
        for wall in self.walls:
            wall.draw(screen)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen)

        # Draw bonuses
        for bonus in self.bonuses:
            bonus.draw(screen)

        # Draw player
        if self.player:
            self.player.draw(screen)