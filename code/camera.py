import pygame.event

from settings import *
from battle_sprites import *
from overworld_sprites import *
from tilemap import *
from button import Button

class CameraGroup(pygame.sprite.Group):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.display_surface = pygame.display.get_surface()

    def draw(self, surface):
        for spr in self.sprites():
            surface.blit(spr.image, self.camera.apply(spr.rect))

class Camera():
    def __init__(self, target, world_size):
        self.target = target
        self.world_size = world_size
        self.offset = pygame.Vector2(0, 0)
        self.screen_center = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)


    def update(self):
        desired_x = self.target.rect.x - self.screen_center.x
        desired_y = self.target.rect.y - self.screen_center.y

        desired_x = max(0, min(desired_x,self.world_size.x - WINDOW_WIDTH))
        desired_y = max(0, min(desired_y, self.world_size.y - WINDOW_HEIGHT))

        self.offset.update(desired_x, desired_y)

    def apply(self, rect_or_pos):
        if hasattr(rect_or_pos, 'x') and hasattr(rect_or_pos, 'y'):
            return rect_or_pos.move(-self.offset)
        else:
            return (rect_or_pos[0] - self.offset.x, rect_or_pos[1] - self.offset.y)

