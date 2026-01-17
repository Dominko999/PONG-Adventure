from settings import *
from global_functions import resource_path

class MusicManager():
    def __init__(self):
        self.music = {
            'overworld' : resource_path(os.path.join('music', 'overworld.ogg')),
            'battle' : resource_path(os.path.join('music', 'battle.ogg'))
        }

        self.sounds = {
            'ball_hit' : resource_path(os.path.join('music', 'ball_hit.ogg')),
            'health_lost' : resource_path(os.path.join('music', 'health_lost.ogg')),
            'typing' : resource_path(os.path.join('music', 'typing.ogg')),
            'button_pressed' : resource_path(os.path.join('music', 'button_pressed.ogg'))
        }

    def play_music(self, music_name):
        pygame.mixer.music.load(self.music[music_name])
        pygame.mixer.music.play(-1)

    def play_sound(self, sound_name):
        sound = pygame.mixer.Sound(self.sounds[sound_name])
        sound.play()