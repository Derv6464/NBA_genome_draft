import random

class DataHandler:
    def __init__(self, player_data, game_data, max_salary):
        self.player_data = player_data
        self.game_data = game_data
        self.max_salary = max_salary
        self.front_court_players = [p for p in player_data if p.get("position") in ["fc"]]
        self.back_court_players = [p for p in player_data if p.get("position") in ["bc"]]
        self.unspecified_players = [p for p in player_data if p.get("position") not in ["fc", "bc"]]
        self.has_no_data = [p for p in self.player_data if not p.get("weekly_stats")]

    def make_random_team(self):
        team = random.sample(self.front_court_players, 5) + random.sample(self.back_court_players, 5)
        return team
    
    def get_team_salary(self, team):
        return sum([float(p.get("salary")) for p in team])
    
    def get_weekly_stats(self, player):
        return player.get("weekly_stats")

    def check_player_per_team(self, team):
        for player in team:
            team_count = sum(1 for p in team if p.get("team") == player.get("team"))
            if team_count > 2:
                return False

        return True

    def check_player_salary(self, team):
        return self.get_team_salary(team) <= self.max_salary
    
    def check_team_validity(self, team):
        return self.check_player_salary(team) and self.check_player_per_team(team)
    
    def make_random_valid_team(self):
        team = self.make_random_team()

        while not self.check_team_validity(team):
            team = self.make_random_team()
            
        return team
    
    def get_players_match_count(self, player, week):

        player_team = player.get("team")
        for team in self.game_data:
            if team.get("abbreviation") == player_team:
                return len(team.get("game_dates").get(str(week)))
    
        return 0

