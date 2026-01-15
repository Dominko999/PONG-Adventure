from settings import *
import json
import pickle

class SaveManager():
    def __init__(self):
        self.game_state = {
            'player_position' : '',
            'level' : 1,
            'exp' : 0,
            'health' : 3,
            'agility' : 5,
            'size' : 4,
            'defeated_enemies' : {}, # their position coordinates stored as a string - [str(x,y)]
            'opened_doors' : {}
        }

        self.current_save_file = 'save1.sav'

    def is_instance_already_cleared(self, instance, list='defeated_enemies'):
        return instance in self.game_state[list]

    def save_game(self):
        pass

    def load_save(self):
        pass