from settings import *
import json, os
from global_functions import get_save_path

class SaveManager():
    def __init__(self):
        self.game_state = {
            'save_name' : 'The beginning',
            'player_position' : (475, 6100),
            'stats' : {
                'level' : 1,
                'exp': 0,
                'health': 3,
                'agility': 5,
                'size': 4
            },
            'defeated_enemies' : {}, # their position coordinates stored as a string - [str(x,y)]
        }
        self.new_game_state = self.game_state.copy()

        self.current_save_file_name = None
        self.current_save_file_path = None

        self.new_game = True

    def is_instance_already_cleared(self, instance, list='defeated_enemies'):
        return instance in self.game_state[list]

    def save_game(self, position, stats, checkpoint_name):
        self.game_state['player_position'] = position
        self.game_state['stats'] = stats
        self.game_state['save_name'] = checkpoint_name
        with open(self.current_save_file_path, 'w') as write_file:
            json.dump(self.game_state, write_file)

    def load_save(self, save_chosen=None):
        if save_chosen is None:
            save_chosen = self.current_save_file_name
        else:
            self.current_save_file_name = save_chosen
        self.current_save_file_path = get_save_path(os.path.join('saves', str(save_chosen + '.json')))
        try:
            with open(self.current_save_file_path, 'r') as read_file:
                self.game_state = json.load(read_file)
                self.new_game = False
        except:
            with open(self.current_save_file_path, 'w') as write_file:
                json.dump(self.new_game_state, write_file)
                self.new_game = True

    def return_save_name(self, save_chosen):
        save_file_path = get_save_path(os.path.join('saves', str(save_chosen + '.json')))
        try:
            with open(save_file_path, 'r') as read_file:
                game_state = json.load(read_file)
                return game_state['save_name']
        except:
            return 'Empty'

    def delete_save_file(self, save_chosen):
        save_file_path = get_save_path(os.path.join('saves', str(save_chosen + '.json')))
        try:
            os.remove(save_file_path)
        except:
            pass