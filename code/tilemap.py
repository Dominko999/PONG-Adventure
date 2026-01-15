import pygame.sprite

from timer import Timer
from pygame import sprite
from settings import *
from pathlib import Path
from pytmx.util_pygame import load_pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, collision = False):
        super().__init__(groups)
        self.image = surf
        self.image = pygame.transform.scale(self.image, (64,64))
        self.rect = self.image.get_frect(topleft=pos)
        if collision:
            self.image.fill(COLORS['paddle_slide'])

class Tilemap():
    def __init__(self):
        super().__init__()
        self.tmx_file = load_pygame(Path(__file__).resolve().parent.parent / 'data' / 'tilemap.tmx')
        self.draw_group = pygame.sprite.Group()
        self.background_group = pygame.sprite.Group()
        self.collision_group = pygame.sprite.Group()
        self.world_size = pygame.Vector2(self.tmx_file.width * 64, self.tmx_file.height * 64)

        self.build()

    def build(self):
        for layer in self.tmx_file.visible_layers:
            if layer.name == 'Background':
                for x,y,surf in layer.tiles():
                    pos = (x * 64, y * 64)
                    Tile(pos, surf, (self.draw_group, self.background_group))
            if layer.name == 'Collision':
                for x,y,surf in layer.tiles():
                    pos = (x * 64, y * 64)
                    Tile(pos, surf, (self.draw_group, self.collision_group))