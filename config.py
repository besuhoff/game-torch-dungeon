import os
from typing import Final

ASSETS_FOLDER: Final = os.path.join('assets')

# Screen settings
SCREEN_WIDTH: Final = 800
SCREEN_HEIGHT: Final = 600

FRAMERATE: Final = 60
DEBUG = False

HEART_TEXTURE: Final = os.path.join(ASSETS_FOLDER, 'heart.png')

# World settings
WALL_TEXTURE: Final = os.path.join(ASSETS_FOLDER, 'wall.jpg')
FLOOR_TEXTURE: Final = os.path.join(ASSETS_FOLDER, 'floor.png')
TORCH_RADIUS: Final = 200
TORCH_SOUND: Final = os.path.join(ASSETS_FOLDER, 'torch.mp3')
GAME_OVER_SOUND: Final = os.path.join(ASSETS_FOLDER, 'game-over.mp3')

# Player settings
PLAYER_SPEED: Final = 5
PLAYER_SIZE: Final = 32
PLAYER_TEXTURE_SIZE: Final = 64
PLAYER_TEXTURE_CENTER: Final = (PLAYER_TEXTURE_SIZE / 2 - 1, 26)
PLAYER_GUN_END: Final = (PLAYER_TEXTURE_SIZE / 2 - 8, 64)
PLAYER_TEXTURE: Final = os.path.join(ASSETS_FOLDER, 'player.png')
PLAYER_LIVES: Final = 5
PLAYER_INVULNERABILITY_TIME: Final = 1 # Seconds of invulnerability after getting hit
PLAYER_HURT_SOUND: Final = os.path.join(ASSETS_FOLDER, 'grunt.mp3')
PLAYER_ROTATION_SPEED: Final = 3  # Degrees per frame
PLAYER_SHOOT_DELAY: Final = 0.2  # Seconds between shots
PLAYER_BULLET_COLOR: Final = (0, 255, 255)  # Cyan bullets for player
PLAYER_MAX_BULLETS: Final = 6  # Maximum number of bullets
PLAYER_BULLET_RECHARGE_TIME: Final = 1.5  # Seconds to recharge one bullet
PLAYER_BULLET_RECHARGE_SOUND: Final = os.path.join(ASSETS_FOLDER, 'weapon-reload.mp3')

# Enemy settings
ENEMY_SPEED: Final = 2
ENEMY_SIZE: Final = 20
ENEMY_TEXTURE_SIZE: Final = 64
ENEMY_TEXTURE_CENTER: Final = (PLAYER_TEXTURE_SIZE / 2 - 1, 26)
ENEMY_GUN_END: Final = (ENEMY_TEXTURE_SIZE / 2 - 1, 64)
ENEMY_TEXTURE: Final = os.path.join(ASSETS_FOLDER, 'enemy.png')
ENEMY_SHOOT_DELAY: Final = 1 # Seconds between shots
ENEMY_HURT_SOUND: Final = os.path.join(ASSETS_FOLDER, 'evil-grunt.mp3')

BULLET_SIZE: Final = 6
BULLET_SPEED: Final = 7
BULLET_SOUND: Final = os.path.join(ASSETS_FOLDER, 'blaster.mp3')

# Aid kit settings
AID_KIT_SIZE: Final = 32
AID_KIT_TEXTURE: Final = os.path.join(ASSETS_FOLDER, 'aid-kit.png')
AID_KIT_HEAL_AMOUNT: Final = 2
AID_KIT_PICKUP_SOUND: Final = os.path.join(ASSETS_FOLDER, 'heal.mp3')
AID_KIT_SPAWN_CHANCE: Final = 0.3  # Chance to spawn aid kit when enemy dies