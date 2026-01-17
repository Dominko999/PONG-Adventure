from settings import *

def write_text(text, font, color, x, y, y_step=0, screen = None, anchor='center'):
    if isinstance(text, str):
        text = text.splitlines()
    for index, line in enumerate(text):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect()
        setattr(text_rect, anchor, (x, y + index * y_step))
        screen.blit(text_surface, text_rect)

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_save_path(relative_path):
    # This gets the directory where the .exe (or .py script) is actually located
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)