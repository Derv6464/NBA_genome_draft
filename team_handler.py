import random
from team import Team

class TeamHandler:
    def __init__(self, player_data, game_data, max_salary):
        self.player_data = player_data
        self.game_data = game_data
        self.max_salary = max_salary
        self.front_court_players = [p for p in player_data if p.get("position") in ["fc"]]
        self.back_court_players = [p for p in player_data if p.get("position") in ["bc"]]
        self.unspecified_players = [p for p in player_data if p.get("position") not in ["fc", "bc"]]
        self.has_no_data = [p for p in self.player_data if not p.get("weekly_stats")]

    def make_team_from_ids(self, ids) -> Team:
        team =[player for player in self.player_data if (player.get("id")) and (player.get("id") in ids)]
        return Team(team, self.game_data)
    
    def make_random_team(self) -> Team:
        team = random.sample(self.front_court_players, 5) + random.sample(self.back_court_players, 5)
        return Team(team, self.game_data)

    def make_random_valid_team(self):
        team = self.make_random_team()

        while not team.check_team_validity():
            team = self.make_random_team()
            
        return team

    def get_best_players(self):
        ''' Depth 1 of "tree" 
        Selects the top 10 players by total points scored
        '''
        player_pool = [(player, int(player.get("total_points"))) for player in self.player_data if player not in self.has_no_data]
        player_pool.sort(key=lambda x: x[1], reverse=True)
        team = [player for player, points in player_pool[:10]]
        return Team(team, self.game_data)
    
    def get_random_no_caps(self):
        ''' Depth 2 of "tree" 
        Selects a random team without salary, position or team caps'''
        team = random.sample(self.player_data, 10)
        return Team(team, self.game_data)
    
    def get_random_position_cap(self):
        ''' Depth 3 of "tree"
        Selects a random team without salary or team caps'''
        team = random.sample(self.front_court_players, 5) + random.sample(self.back_court_players, 5)
        return Team(team, self.game_data)
    
    def get_random_team_cap(self):
        ''' Depth 4 of "tree"
        Selects a random team without salary cap'''
        valid_team = False
        while not valid_team:
            team = self.get_random_no_caps()
            valid_team = team.check_player_per_team()
        return team
    
    def get_random_salary_cap(self):
        ''' Depth 5 of "tree"
        Selects a random team without team or position caps'''
        valid_team = False
        while not valid_team:
            team = self.get_random_no_caps()
            valid_team = team.check_player_salary()
        return team
