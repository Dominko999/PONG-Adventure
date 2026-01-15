import pygame
from settings import *

class TextBox(pygame.sprite.Sprite):
    def __init__(self, groups, text, mode='dialogue'):
        super().__init__(groups)
        self.text = text
        self.mode = mode

        self.line = 0
        self.active = True

        # white outline, used as main image
        self.image = pygame.Surface((910, 160), pygame.SRCALPHA)
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 6 * 5))
        self.image.fill(COLORS['paddle_active'])

        # black background
        self.background_image = pygame.Surface((900, 150), pygame.SRCALPHA)
        self.background_rect = self.background_image.get_frect(center=(self.image.get_width()/2, self.image.get_height()/2))
        self.background_image.fill(COLORS['bg'])

        # text
        self.text_surf = FONTS['dialogue'].render(str(text[0]), True, COLORS['paddle_active'])
        self.text_rect = self.text_surf.get_frect(center=(self.image.get_width()/2, self.image.get_height()/2-5))


        self.background_image.blit(self.text_surf, self.text_rect)
        self.image.blit(self.background_image, self.background_rect)

    def next_line(self):
        self.line += 1
        if self.line < len(self.text):
            self.text_surf = FONTS['dialogue'].render(str(self.text[self.line]), True, COLORS['paddle_active'])
            self.text_rect = self.text_surf.get_frect(
                center=(self.image.get_width() / 2, self.image.get_height() / 2 - 5))
            self.background_image.fill(COLORS['bg'])
            self.background_image.blit(self.text_surf, self.text_rect)
            self.image.blit(self.background_image, self.background_rect)
        else:
            self.active = False
            self.kill()

