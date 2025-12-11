import random
from team import Team

class TeamHandler:
    def __init__(self, player_data: list, game_data:dict, max_salary: int, generate_team_for_week: int):
        self.player_data = player_data
        self.game_data = game_data
        self.max_salary = max_salary
        self.front_court_players = [p for p in player_data if p.get("position") in ["fc"]]
        self.back_court_players = [p for p in player_data if p.get("position") in ["bc"]]
        self.unspecified_players = [p for p in player_data if p.get("position") not in ["fc", "bc"]]
        self.has_no_data = [p for p in self.player_data if not p.get("weekly_stats")]
        self.generate_team_for_week = generate_team_for_week

        self.fitness_func = None

    def update_fitness_function(self, fitness_func):
        self.fitness_func = fitness_func

    def make_team_from_ids(self, ids: list[str], skip_team_creation=False) -> Team | list[dict]:
        team =[player for player in self.player_data if (player.get("id")) and (player.get("id") in ids)]

        if skip_team_creation:
            return team  # Return just the player list
        return Team(team, self.game_data, self.generate_team_for_week, self.fitness_func)

    
    def _make_random_team(self) -> Team:
        team = random.sample(self.front_court_players, 5) + random.sample(self.back_court_players, 5)
        return Team(team, self.game_data, self.generate_team_for_week, self.fitness_func)

    def make_random_valid_team(self) -> Team:
        team = self._make_random_team()

        while not team.check_team_validity():
            team = self._make_random_team()
            
        return team