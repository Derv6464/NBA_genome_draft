import random

class DataHandler:
    def __init__(self, player_data, game_data):
        self.player_data = player_data
        self.game_data = game_data

    def make_random_team(self):
        #need to do front court, back court, etc.
        return random.sample(self.player_data, 5)