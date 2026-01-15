from settings import *

def write_text(text, font, color, x, y, y_step=0, screen = None, anchor='center'):
    if isinstance(text, str):
        text = text.splitlines()
    for index, line in enumerate(text):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect()
        setattr(text_rect, anchor, (x, y + index * y_step))
        screen.blit(text_surface, text_rect)