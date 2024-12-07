import pygame
import config
from screen_object import ScreenObject
from world import World

class AidKit(ScreenObject):
    def __init__(self, world: World, world_x: float, world_y: float):
        super().__init__(world, world_x, world_y, config.AID_KIT_SIZE, config.AID_KIT_SIZE)
        self.pickup_sound = pygame.mixer.Sound(config.AID_KIT_PICKUP_SOUND)
        self.active = True
        
        try:
            aid_surface = pygame.image.load(config.AID_KIT_TEXTURE).convert_alpha()
            self.surface = pygame.transform.scale(aid_surface, (config.AID_KIT_SIZE, config.AID_KIT_SIZE))
        except pygame.error:
            print("Could not load aid kit texture")
            self.surface = None
            
    def check_player_pickup(self) -> bool:
        """Check if player picks up the aid kit"""
        player = self._world.player
        if not self.active or not player:
            return False
        
        player_rect = player.get_collision_rect()
        
        if (self.check_collision(*player_rect)):
            self.pickup_sound.play()
            player.heal(config.AID_KIT_HEAL_AMOUNT)
            self.active = False
            return True
            
        return False
            
    def draw(self, screen: pygame.Surface):
        if not self.active or not self.surface:
            return
            
        screen_x, screen_y = self.get_screen_coordinates()
        screen.blit(self.surface, (screen_x - config.AID_KIT_SIZE / 2, 
                                 screen_y - config.AID_KIT_SIZE / 2))
