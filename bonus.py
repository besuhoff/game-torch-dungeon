import pygame, random, config
from screen_object import ScreenObject
from world import World

BONUS_TYPE_AID_KIT = "aid_kit"
BONUS_TYPE_GOGGLES = "goggles"

class Bonus(ScreenObject):
    def __init__(self, world: World, world_x: float, world_y: float):
        super().__init__(world, world_x, world_y, config.AID_KIT_SIZE, config.AID_KIT_SIZE)
        self.pickup_sound = pygame.mixer.Sound(config.BONUS_PICKUP_SOUND)
        self.active = True
        self.type = random.choices([BONUS_TYPE_AID_KIT, BONUS_TYPE_GOGGLES], weights=[5, 1], k=1)[0]
        
        try:
            if self.type == BONUS_TYPE_AID_KIT:
                self.surface = pygame.image.load(config.AID_KIT_TEXTURE).convert_alpha()
                self.surface = pygame.transform.scale(self.surface, (config.AID_KIT_SIZE, config.AID_KIT_SIZE))
            elif self.type == BONUS_TYPE_GOGGLES:
                self.surface = pygame.image.load(config.GOGGLES_TEXTURE).convert_alpha()
                self.surface = pygame.transform.scale(self.surface, (config.GOGGLES_SIZE, config.GOGGLES_SIZE))
        
        except pygame.error:
            self.surface = None
        
    def check_player_pickup(self) -> bool:
        """Check if player picks up the aid kit"""
        player = self._world.player
        if not self.active or not player:
            return False
        
        player_rect = player.get_collision_rect()
        
        if (self.check_collision(*player_rect)):
            if self.type == BONUS_TYPE_AID_KIT:
                player.heal(config.AID_KIT_HEAL_AMOUNT)
            elif self.type == BONUS_TYPE_GOGGLES:
                player.start_night_vision()

            self.pickup_sound.play()
            self.active = False
            return True
            
        return False
            
    def draw(self, screen: pygame.Surface):
        if not self.active or not self.surface:
            return
            
        screen_x, screen_y = self.get_screen_coordinates()
        screen.blit(self.surface, (screen_x - config.AID_KIT_SIZE / 2, 
                                 screen_y - config.AID_KIT_SIZE / 2))

    def update(self):
        if self.check_player_pickup():
            self._world.bonuses.remove(self)