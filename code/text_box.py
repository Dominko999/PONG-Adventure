import pygame
from settings import *
from timer import Timer
from animation import AnimatedSprite

class TextBox(pygame.sprite.Sprite):
    def __init__(self, groups, text, character_name='', mode='dialogue'):
        super().__init__(groups)
        self.text = text
        self.mode = mode

        self.line = 0
        self.active = True

        self.letter_timer = Timer(0.01,lambda: self.write_letter(), repeat=True)
        self.button_actvated_timer = Timer(0.06,lambda: self.button_next_frame(), repeat=False)
        self.letter_index = 0
        self.line_to_blit = ''

        if self.mode == 'dialogue':
            # background
            self.animated_sprite = AnimatedSprite('dialogue_box', 1, (1088, 216), 0)
            self.image = self.animated_sprite.frames[0].copy()
            self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 6 * 5))

            # npc name
            self.name_text_surf = FONTS['dialogue'].render(str(character_name), True, COLORS['paddle_active'])
            self.name_text_rect = self.name_text_surf.get_frect(midleft=(self.image.get_width()/13, self.image.get_height()/9))

            self.image.blit(self.name_text_surf, self.name_text_rect)

        if self.mode == 'text':
            # background
            self.animated_sprite = AnimatedSprite('text_box', 1, (1088, 216), 0)
            self.image = self.animated_sprite.image.copy()
            self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 6 * 5))

        # E button
        self.e_button = AnimatedSprite('E_button', 2, (64, 64), 0)
        self.e_button.rect.bottomright = (self.image.get_width() - 16, self.image.get_height()-16)


        # text
        self.text_surf = FONTS['dialogue'].render(str(self.text[self.line]), True, COLORS['paddle_active'])
        self.text_rect = self.text_surf.get_frect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.letter_timer.activate()


    def write_letter(self):
        full_line = self.text[self.line]
        if self.letter_index < len(full_line):
            self.line_to_blit = self.line_to_blit + str(full_line[self.letter_index])
            self.text_surf = FONTS['dialogue'].render(str(full_line), True, COLORS['paddle_active'])
            self.text_rect = self.text_surf.get_frect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
            self.text_surf = FONTS['dialogue'].render(self.line_to_blit, True, COLORS['paddle_active'])
            if self.mode == 'dialogue':
                self.redraw_dialogue()
            if self.mode == 'text':
                self.redraw_text()
            self.letter_index += 1
        else:
            self.letter_timer.terminate()


    def next_line(self):
        self.line += 1
        self.button_actvated_timer.activate()
        self.button_next_frame()
        if self.line < len(self.text):
            #refreshes text and proceeds to redraw according to mode
            self.letter_index = 0
            self.line_to_blit = ''
            self.letter_timer.activate() # activates the timer, update function sees it and starts calling animate_writing function every frame

        else:
            self.active = False
            self.kill()

    def redraw_dialogue(self):
        self.image = self.animated_sprite.frames[0].copy()

        self.image.blit(self.name_text_surf, self.name_text_rect)
        self.image.blit(self.text_surf, self.text_rect)
        self.image.blit(self.e_button.image, self.e_button.rect)

    def redraw_text(self):
        self.image = self.animated_sprite.frames[0].copy()

        self.image.blit(self.text_surf, self.text_rect)
        self.image.blit(self.e_button.image, self.e_button.rect)

    def button_next_frame(self):
        self.e_button.index += 1
        self.e_button.image = self.e_button.frames[int(self.e_button.index) % len(self.e_button.frames)]

    def update(self, dt):
        self.letter_timer.update()
        self.button_actvated_timer.update()