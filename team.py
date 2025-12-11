from datetime import datetime
from schedule import Schedule

class Team:
    def __init__(self, players: list, schedule: Schedule, generate_team_for_week, fitness_func=None):
        self.players = players
        self.schedule = schedule
        self.valid_team = self.check_team_validity()
        self.salary = self._get_team_salary()
        self.generate_team_for_week = generate_team_for_week
        self.fitness_func = fitness_func
        if fitness_func:
            self.fitness = fitness_func(self)
        else:
            self.fitness = self._calculate_fitness()

    def re_evaluate(self):
        self.valid_team = self.check_team_validity()
        self.salary = self._get_team_salary()
        self.fitness = self.fitness

    def get_week_score(self, week) -> int:
        ''' Returns the total points scored by all players in the team for a given week '''
        return sum(player["weekly_stats"][str(week)]["total_point"] for player in self.players if player.get("weekly_stats"))
    
    def _get_team_salary(self) -> float:
        ''' Returns the total salary of all players in the team '''
        return sum([float(p.get("salary")) for p in self.players])
        
    def _get_weekly_stats(self, player: dict) -> dict:
        ''' Returns the weekly stats of a player '''
        return player.get("weekly_stats")   
    
    def _get_players_match_count(self, player: dict, week: int) -> int:
        player_team = player.get("team")
        self.schedule.get_team_days(player_team, week)
    
        return len(self.schedule.get_team_days(player_team, week))
    
    def _get_players_playing_on_day(self, week: int, day: int) -> list[dict]:
        '''Return all players who play on a specific day.'''
        playing = []
        for p in self.players:
            team = p.get("team")
            days = self.schedule.get_team_days(team, week)
            if day in days:
                playing.append(p)
        return playing

    def _get_max_active_players(self, week: int, day: int) -> list[dict]:
        '''Return the maximum valid lineup for that specific day.'''
    
        players_today = self._get_players_playing_on_day(week, day)

        fc = [p for p in players_today if p["position"] == "fc"]
        bc = [p for p in players_today if p["position"] == "bc"]

        selected_fc = fc[:2] if len(fc) >= 2 else fc
        selected_bc = bc[:2] if len(bc) >= 2 else bc

        used_ids = {id(p) for p in selected_fc + selected_bc}
        remaining = [p for p in players_today if id(p) not in used_ids]

        flex = remaining[:1] if remaining else []
        lineup = selected_fc + selected_bc + flex

        return lineup
    
    def get_max_score(self, week:int, day:int) -> int:
        '''Return the maximum score for that specific day.'''
        players_today = self._get_players_playing_on_day(week, day)

        fc = [p for p in players_today if p["position"] == "fc" if p['weekly_stats'].get(str(week))]
        bc = [p for p in players_today if p["position"] == "bc" if p['weekly_stats'].get(str(week))]

        fc_scores = [(player, self.get_game_score(player['weekly_stats'][str(week)]["game_stats"][str(day)][0])) if (len(player['weekly_stats'][str(week)]["game_stats"][str(day)]) > 0) else (player, 0) for player in fc]
        bc_scores = [(player, self.get_game_score(player['weekly_stats'][str(week)]["game_stats"][str(day)][0])) if (len(player['weekly_stats'][str(week)]["game_stats"][str(day)]) > 0) else (player, 0) for player in bc]

        fc_scores.sort(key=lambda x: x[1], reverse=True)
        bc_scores.sort(key=lambda x: x[1], reverse=True)
       
        selected_fc = fc_scores[:2] if len(fc) >= 2 else fc_scores
        selected_bc = bc_scores[:2] if len(bc) >= 2 else bc_scores

        used_ids = {id(p[0]) for p in selected_fc + selected_bc}

        remaining = [p for p in players_today if id(p) not in used_ids and p['weekly_stats'].get(str(week))]
        remaining_scores = [(player, self.get_game_score(player['weekly_stats'][str(week)]["game_stats"][str(day)][0])) if (len(player['weekly_stats'][str(week)]["game_stats"][str(day)]) > 0) else (player, 0) for player in remaining]
        flex = max(remaining_scores, key=lambda x: x[1:]) if remaining_scores else (None, 0)

        total = sum(p[1] for p in selected_fc) + sum(p[1] for p in selected_bc) + flex[1]

        return total

    def get_game_score(self, game_stats: list) -> int:
        ''' ["Minutes","Field Goals Made-Attempted","Field Goal Percentage","3-Point Field Goals Made-Attempted",
            "3-Point Field Goal Percentage","Free Throws Made-Attempted","Free Throw Percentage","Rebounds","Assists",
            "Blocks","Steals","Fouls","Turnovers","Points"
        '''
        total_points = int(game_stats[13])
        total_rebounds = int(game_stats[7])
        total_assists = int(game_stats[8])
        total_steals = int(game_stats[10])
        total_blocks = int(game_stats[9])

        fantasy_points = (total_points + total_rebounds + (total_assists*2) + (total_steals*3) + (total_blocks*3))
        return fantasy_points

    def copy(self) -> 'Team':
        return Team(self.players.copy(), self.schedule, self.generate_team_for_week, self.fitness_func)
    
    def check_player_per_team(self) -> bool:
        for player in self.players:
            team_count = sum(1 for p in self.players if p.get("team") == player.get("team"))
            if team_count > 2:
                return False
        return True

    def check_player_salary(self, salary = 100) -> bool:
        return self._get_team_salary() <= salary
    
    def check_player_position(self) -> bool:
        front_court_count = sum(1 for p in self.players if p.get("position") == "fc")
        back_court_count = sum(1 for p in self.players if p.get("position") == "bc")
        return front_court_count == 5 and back_court_count == 5
    
    def check_team_validity(self) -> bool:
        return self.check_player_salary() and self.check_player_per_team() and self.check_player_position()
    
    def _calculate_fitness(self, salary_cap = 100) -> float:
        salary_penalty = self._get_salary_penalty(salary_cap)
        games_penalty = self._get_range_games_penalty(self.generate_team_for_week-1, self.generate_team_for_week) #only want week 6 team, so limit games penalty to weeks 1-6

        position_penalty = self._get_invalid_position_penalty() 
        duplication_penalty = self._get_duplicate_players_penalty() #if player appears more than once in team

        player_scores = [self._get_player_score(player) for player in self.players]
        total_game_weeks = self._get_total_game_weeks(player_scores) #commenting out to get an accurate week 6 perdiction

        if total_game_weeks > self.generate_team_for_week-1:
            total_game_weeks = self.generate_team_for_week-1

        weighted_scores = self._weight_weeks(player_scores, total_game_weeks)
        total_weighted_score = sum(weighted_scores)

        team_count_penalty = self._get_team_count_penalty()
        not_playing_penalty = self._get_no_data_players_penalty()

        fitness_score = total_weighted_score - salary_penalty - games_penalty - team_count_penalty - position_penalty - duplication_penalty - not_playing_penalty

        return fitness_score

    def _weight_weeks(self, player_scores: list, total_weeks: int) -> list[float]:
        scores = []
        for player in player_scores:
            score = 0.0
            if player is None:
                scores.append(0.0)
                continue
            
            for week in range(1, total_weeks + 1):
                week_str = str(week)
                if week_str not in player:
                    score+= 0.0
                    continue
                week_score = player.get(week_str, 0)
                weight = week / total_weeks  
                score += week_score * weight
            scores.append(score)
        return scores

    def _get_total_game_weeks(self, player_scores: list) -> int:
        max_weeks = 0
        for player_data in player_scores:  
            if not player_data:
                continue  
            last_key = max(int(week) for week in player_data.keys())
            if last_key > max_weeks:
                max_weeks = last_key
        return max_weeks

    def _get_player_score(self, player: dict) -> dict | None:
        stats = self._get_weekly_stats(player)
        filtered_weeks = {}
        for week, data in stats.items():
            if data['total_point'] != 0: 
                filtered_weeks[week] = data['total_point']
        
        return filtered_weeks if filtered_weeks else None
    
    def _get_weekly_games_penalty(self, week: int) -> int:
        '''Calculate penalty based on number of games played in a week.'''
        total_penalty = 0
        for day in range(1, 8):
            active_players = self._get_max_active_players(week, day)
            total_penalty += max(0, 5 - len(active_players))

        return total_penalty
    
    def _get_range_games_penalty(self, start_week: int, end_week: int) -> int:
        '''Calculate total games penalty across a range of weeks.'''
        total_penalty = 0
        for week in range(start_week, end_week + 1):
            total_penalty += self._get_weekly_games_penalty(week)
        return total_penalty
    
    def _get_total_games_penalty(self) -> int:
        '''Calculate total games penalty across all weeks.'''
        return self.get_range_games_penalty(1, 26)
    
    def _get_duplicate_players_penalty(self) -> int:
        '''Calculate penalty for duplicate players in the team.'''
        duplication_penalty = 0
        for player in self.players:
            apperances_on_teams = sum(1 for p in self.players if p.get("id") == player.get("id"))
            if apperances_on_teams > 1:
                duplication_penalty += 100
        return duplication_penalty
    
    def _get_invalid_position_penalty(self) -> int:
        '''Calculate penalty for invalid player positions in the team.'''
        position_penalty = 0
        fc_count = sum(1 for p in self.players if p.get("position") == "fc")
        bc_count = sum(1 for p in self.players if p.get("position") == "bc")
        if fc_count != 5:
            position_penalty += abs(fc_count - 5) * 50
        if bc_count != 5:
            position_penalty += abs(bc_count - 5) * 50

        return position_penalty
    
    def _get_salary_penalty(self, salary_cap) -> int:
        '''Calculate penalty based on team salary exceeding the cap.'''
        if self._get_team_salary() > salary_cap:
            return (self._get_team_salary() - salary_cap) * 150
        return 0
    
    def _get_team_count_penalty(self) -> int:
        '''Calculate penalty for exceeding player count per team.'''
        if self.check_player_per_team():
            return 0
        return 200
    
    def _get_no_data_players_penalty(self) -> int:
        '''Returns a list of players with no data in the team.'''
        no_data_players = [player for player in self.players if not player.get("weekly_stats")]
        return len(no_data_players) * 100
    
    def save_team(self, file_path="data/team_output.json"):
        '''Saves the team data to a specified JSON file.'''
        import json

        data = {
            "run" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fitness": self._calculate_fitness(),
            "salary": self._get_team_salary(),
            "players": [player.get("id") for player  in self.players]
        }
        with open(file_path, 'a', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            f.write('\n') 