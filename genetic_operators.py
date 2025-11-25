from data_handler import DataHandler
import random

class GeneticOperators:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def filter_by_position_and_salary(self, position, remaining_salary):
        if position == "fc":
            candidates = self.data_handler.front_court_players
        elif position == "bc":
            candidates = self.data_handler.back_court_players

        candidates = [p for p in candidates if float(p.get("salary")) <= remaining_salary]
        return candidates

    def filter_by_team_limit(self, candidates, current_teams, max_per_team=2):
        def valid_team(player):
            return current_teams.count(player.get("team")) < max_per_team
        return [p for p in candidates if valid_team(p)]

    def mutate(self, team):
        team_size = len(team)
        team_salary = sum(float(p.get("salary")) for p in team)

        random_player_index = random.randint(0, team_size - 1)
        player_to_replace = team[random_player_index]
        player_position = player_to_replace.get("position")
        player_salary = float(player_to_replace.get("salary"))
        remaining_salary = self.data_handler.max_salary - (team_salary - player_salary)

        candidates = self.filter_by_position_and_salary(player_position, remaining_salary)

        current_teams = [p.get("team") for i, p in enumerate(team) if i != random_player_index]
        candidates = self.filter_by_team_limit(candidates, current_teams)

        if not candidates:
            return team

        new_player = random.choice(candidates)
        new_team = team.copy()
        new_team[random_player_index] = new_player

        return new_team
