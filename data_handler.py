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
    
    def check_player_per_team(self, team):
        for player in team:
            team_count = sum(1 for p in team if p.get("team") == player.get("team"))
            if team_count > 2:
                return False

        return True

    def check_player_salary(self, team):
        return self.get_team_salary(team) <= self.max_salary
    
    def check_player_position(self, team):
        front_court_count = sum(1 for p in team if p.get("position") == "fc")
        back_court_count = sum(1 for p in team if p.get("position") == "bc")
        return front_court_count == 5 and back_court_count == 5
    
    def check_team_validity(self, team):
        return self.check_player_salary(team) and self.check_player_per_team(team) and self.check_player_position(team)
    
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

    def get_best_players(self):
        ''' Depth 1 of "tree" 
        Selects the top 10 players by total points scored
        '''
        player_pool = [(player, int(player.get("total_points"))) for player in self.player_data if player not in self.has_no_data]
        player_pool.sort(key=lambda x: x[1], reverse=True)
        team = [player for player, points in player_pool[:10]]
        return team
    
    def get_random_no_caps(self):
        ''' Depth 2 of "tree" 
        Selects a random team without salary, position or team caps'''
        team = random.sample(self.player_data, 10)
        return team
    
    def get_random_position_cap(self):
        ''' Depth 3 of "tree"
        Selects a random team without salary or team caps'''
        team = random.sample(self.front_court_players, 5) + random.sample(self.back_court_players, 5)
        return team
    
    def get_random_team_cap(self):
        ''' Depth 4 of "tree"
        Selects a random team without salary cap'''
        valid_team = False
        while not valid_team:
            team = random.sample(self.player_data, 10)
            valid_team = self.check_player_per_team(team)
        return team
    
    def get_random_salary_cap(self):
        ''' Depth 5 of "tree"
        Selects a random team without team or position caps'''
        valid_team = False
        while not valid_team:
            team = random.sample(self.player_data, 10)
            valid_team = self.check_player_salary(team)
        return team

