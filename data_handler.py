import random

class DataHandler:
    def __init__(self, player_data, game_data):
        self.player_data = player_data
        self.game_data = game_data
        self.front_court_players = [p for p in player_data if p.get("position") in ["C", "F", "PF"]]
        self.back_court_players = [p for p in player_data if p.get("position") in ["G"]]
        self.unspecified_players = [p for p in player_data if p.get("position") not in ["C", "F", "G", "PF"]]
        self.has_data = [p for p in self.unspecified_players if p.get("weekly_stats")]


    def make_random_team(self):
        #need to do front court, back court, etc.
        team = random.sample(self.front_court_players, 2) + random.sample(self.back_court_players, 2)
        if random.randint(0, 100) % 2 == 0:
            team += random.sample(self.front_court_players, 1)
        else:
            team += random.sample(self.back_court_players, 1)
        return team