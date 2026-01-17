import pygame

from settings import *

class Button(pygame.sprite.Sprite):
    def __init__(self, groups, text, font_name, font_color, x, y, width, height, func, parent_surface):
        super().__init__(groups)
        self.text = text
        self.func = func
        self.parent_surface = parent_surface

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_frect(center=(x, y))

        self.text_surf = FONTS[font_name].render(str(text), True, COLORS[font_color])
        self.text_rect = self.text_surf.get_frect(center=(self.image.get_width()/2, self.image.get_height()/2))

        self.pressed_last = False
        self._armed = False

    def change_color(self, mouse_pos, hovering, pressing):
        self.image.fill(COLORS['button'])
        if hovering:
            self.image.fill(COLORS['button_hover'])
            if pressing:
                self.image.fill(COLORS['button_pressed'])

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        hovering = self.rect.collidepoint(mouse_pos)
        pressing = pygame.mouse.get_pressed(num_buttons=3)[0]

        self.change_color(mouse_pos, hovering, pressing)


        if hovering and pressing and not self.pressed_last:
            self._armed = True

        if self._armed and not pressing:
            if hovering:
                self.func()
            self._armed = False

        self.pressed_last = pressing

        self.image.blit(self.text_surf, self.text_rect)