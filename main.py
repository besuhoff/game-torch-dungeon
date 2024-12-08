from calendar import c
from pydoc import text
from sys import flags, platform
import pygame
from bonus import Bonus
import config
from player import Player
from wall import Wall
from enemy import Enemy
import asyncio

from world import World

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
STONE_GRAY = (100, 100, 100)
WALL_BROWN = (139, 69, 19)

def draw_panel(screen: pygame.Surface, world: World):
    if not world.player:
        return

    # Draw lives
    font = pygame.font.Font(None, 24)
    label = font.render("Lives:", True, (255, 255, 255))
    heart_texture = pygame.image.load(config.HEART_TEXTURE)
    heart_texture = pygame.transform.scale(heart_texture, (16, 16))
    screen.blit(label, (10, 10))
    for i in range(world.player.lives):
        screen.blit(heart_texture, (72 + i * 24, 10))

    # Draw kills
    kills_text = font.render(f"Rewards: {world.player.kills * 10}$", True, (255, 255, 0))
    screen.blit(kills_text, (10, 32))

    # Draw bullets
    bullets_text = font.render(f"Bullets: {world.player.bullets_left * 'I'}", True, (0, 255, 255))
    screen.blit(bullets_text, (10, 54))

    # Draw night vision
    if world.player.night_vision_timer > 0:
        night_vision_text = font.render(f"Night Vision: {int(world.player.night_vision_timer)}", True, (0, 255, 0))
        screen.blit(night_vision_text, (10, 76))

async def main():
    world = World(Player, Enemy, Wall, Bonus)
    if platform == "emscripten":
        flags = 0
    else:
        flags = pygame.SCALED | pygame.RESIZABLE

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), flags)
    pygame.display.set_caption("Torch Dungeon")
    clock = pygame.time.Clock()

    # Load floor texture
    try:
        floor_texture = pygame.image.load(config.FLOOR_TEXTURE)
        # Scale the texture to screen size but make it larger for scrolling
        floor_texture = pygame.transform.scale(floor_texture, (config.SCREEN_WIDTH * 0.5, config.SCREEN_HEIGHT * 0.5))
        
    except pygame.error:
        print("Could not load floor texture. Using default color.")
        floor_texture = None

    # Start the game
    world.start_game()

    running = True
    prev_time = pygame.time.get_ticks()
    while running:
        # Calculate delta time in seconds
        current_time = pygame.time.get_ticks()
        world.dt = (current_time - prev_time) / 1000.0  # Convert to seconds
        prev_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.scancode == 21 and world.is_game_over():  # Press R to restart (scancode 21 is 'R' key)
                    world.start_game()

                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_F3:
                    config.DEBUG = not config.DEBUG

        if not world.is_game_over():
            # Player movement
            keys = pygame.key.get_pressed()
            forward = 0
            rotation = 0
            
            # Forward/backward movement
            if keys[pygame.K_w] or keys[pygame.K_UP]: forward += 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: forward -= 1
            
            # Rotation
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: rotation -= 1.5
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: rotation += 1.5

            if world.player:
                world.player.move(forward)
                world.player.rotate(rotation)
                
                # Shooting
                if keys[pygame.K_SPACE]:
                    world.player.shoot()

        # Draw everything
        screen.fill((0, 0, 0))
        
        # Draw floor texture
        if floor_texture:
            # Calculate floor texture position based on world offset
            texture_x = (world.offset_x % floor_texture.get_width()) - floor_texture.get_width()
            texture_y = (world.offset_y % floor_texture.get_height()) - floor_texture.get_height()
            
            # Draw floor tiles
            for y in range(-1, config.SCREEN_HEIGHT // floor_texture.get_height() + 2):
                for x in range(-1, config.SCREEN_WIDTH // floor_texture.get_width() + 2):
                    screen.blit(floor_texture, 
                              (texture_x + x * floor_texture.get_width(),
                               texture_y + y * floor_texture.get_height()))
        else:
            screen.fill(STONE_GRAY)

        world.draw(screen)
        
        # Draw UI
        if world.player:
            draw_panel(screen, world)

        if world.is_game_over():
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over', True, (255, 0, 0))
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2))
            screen.blit(text, text_rect)
            
            font = pygame.font.Font(None, 36)
            text = font.render('Press R to restart', True, (255, 255, 255))
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2 + 50))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(config.FRAMERATE)

        world.update()

        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
