import pygame.event

from settings import *
from battle_sprites import *
from overworld_sprites import *
from tilemap import *
from button import Button

class ProgressBar(pygame.sprite.Sprite):
    def __init__(self, groups, max_value, multiplier, color, x, y, anchor):
        super().__init__(groups)
        self.length = max_value * multiplier
        self.multiplier = multiplier
        self.background_image = pygame.Surface((self.length, self.multiplier))
        self.rect = self.background_image.get_frect()
        if anchor == 'left':
            self.rect.midleft = (x, y)
        elif anchor == 'right':
            self.rect.midright = (x, y)
        elif anchor == 'center':
            self.rect.center = (x, y)
        self.foreground_rect = self.rect.copy()
        self.color = color
        self.background_image.fill(self.color)
        self.create_outlines()
        self.blit_background()
        self.blit_foreground(max_value)

    def create_outlines(self):
        self.image = pygame.Surface((self.rect.size[0] + 10, self.rect.size[1] + 10 ))
        self.image.fill('white')

    def blit_background(self):
        self.background_image.fill(COLORS['progress_bar_background'])
        self.image.blit(self.background_image, (5, 5))

    def blit_foreground(self, value):
        self.foreground_rect = self.rect.copy()
        self.foreground_image = pygame.Surface((value * self.multiplier, self.multiplier))
        self.foreground_image.fill(self.color)
        self.image.blit(self.foreground_image, (5, 5))

    def update_progress_bar(self, value):
        self.blit_background()
        self.blit_foreground(value)