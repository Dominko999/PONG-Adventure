from settings import *
import json
from pathlib import Path

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

        self.current_save_file_name = None
        self.current_save_file_path = None

    def is_instance_already_cleared(self, instance, list='defeated_enemies'):
        return instance in self.game_state[list]

    def save_game(self):
        with open(self.current_save_file_path, 'w') as write_file:
            json.dump(self.game_state, write_file)

    def load_save(self, save_chosen):
        self.current_save_file_name = save_chosen
        self.current_save_file_path = Path(__file__).resolve().parent.parent / 'saves' / str(
            save_chosen + '.json')
        try:
            with open(self.current_save_file_path, 'r') as read_file:
                self.game_state = json.load(read_file)
        except:
            with open(self.current_save_file_path, 'w') as write_file:
                json.dump(self.game_state, write_file)