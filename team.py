from datetime import datetime

class Team:
    def __init__(self, players: list, schedule):
        self.players = players
        self.schedule = schedule
        self.valid_team = self.check_team_validity()
        self.salary = self.get_team_salary()
        self.fitness = self.calculate_fitness()

    def re_evaluate(self):
        self.valid_team = self.check_team_validity()
        self.salary = self.get_team_salary()
        self.fitness = self.calculate_fitness()

    def get_weeks_scores(self, start = 1, end=6):
        ''' Returns a list of all points scored from all players in the team for each week in the range '''
        scores = [0 for _ in range(26)]
        for week in range(start, end + 1):
            scores[week-1] = self.get_week_score(week)
        
        return scores
    
    def get_week_score(self, week):
        ''' Returns the total points scored by all players in the team for a given week '''
        return sum(player["weekly_stats"][str(week)]["total_point"] for player in self.players if player.get("weekly_stats"))
    
    def get_team_salary(self):
        ''' Returns the total salary of all players in the team '''
        return sum([float(p.get("salary")) for p in self.players])
        
    def get_weekly_stats(self, player):
        ''' Returns the weekly stats of a player '''
        return player.get("weekly_stats")
    
    def get_players_match_count(self, player, week):
        player_team = player.get("team")
        self.schedule.get_team_days(player_team, week)
    
        return len(self.schedule.get_team_days(player_team, week))
    
    def get_players_playing_on_day(self, week, day):
        '''Return all players who play on a specific day.'''
        playing = []
        for p in self.players:
            team = p.get("team")
            days = self.schedule.get_team_days(team, week)
            if day in days:
                playing.append(p)
        return playing

    def get_max_active_players(self, week, day):
        '''Return the maximum valid lineup for that specific day.'''
    
        players_today = self.get_players_playing_on_day(week, day)

        fc = [p for p in players_today if p["position"] == "fc"]
        bc = [p for p in players_today if p["position"] == "bc"]

        selected_fc = fc[:2] if len(fc) >= 2 else fc
        selected_bc = bc[:2] if len(bc) >= 2 else bc

        used_ids = {id(p) for p in selected_fc + selected_bc}
        remaining = [p for p in players_today if id(p) not in used_ids]

        flex = remaining[:1] if remaining else []

        lineup = selected_fc + selected_bc + flex

        return lineup
    
    def get_max_score(self, week, day):
        players_today = self.get_players_playing_on_day(week, day)

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

        #need to debug matchs being sorted into days laters
        #for p in selected_fc:
        #    print(f"FC: {p[0]['name']} - {p[1]} points")
        #for p in selected_bc:
        #    print(f"BC: {p[0]['name']} - {p[1]} points")
        #if flex[0]:
        #    print(f"Flex: {flex[0]['name']} - {flex[1]} points")
    


        return total


        #print(f"Week {week}, Day {day} FC Scores: {fc_scores}")
        #print(f"Week {week}, Day {day} BC Scores: {bc_scores}")

        

    def get_game_score(self, game_stats):
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

    def copy(self):
        return Team(self.players.copy(), self.schedule)
    
    def check_player_per_team(self):
        for player in self.players:
            team_count = sum(1 for p in self.players if p.get("team") == player.get("team"))
            if team_count > 2:
                return False
        return True

    def check_player_salary(self, salary = 100):
        return self.get_team_salary() <= salary
    
    def check_player_position(self):
        front_court_count = sum(1 for p in self.players if p.get("position") == "fc")
        back_court_count = sum(1 for p in self.players if p.get("position") == "bc")
        return front_court_count == 5 and back_court_count == 5
    
    def check_team_validity(self):
        return self.check_player_salary() and self.check_player_per_team() and self.check_player_position()
    
    def calculate_fitness(self, salary_cap = 100):
        salary_penalty = self.get_salary_penalty(salary_cap) #penality on salary
        games_penalty = self.get_total_games_penalty() #penality on number of games played
        #games_penalty = self.get_range_games_penalty(1, 6)

        position_penalty = self.get_invalid_position_penalty() 
        duplication_penalty = self.get_duplicate_players_penalty() #if player appears more than once in team

        #game_counts = [self.get_players_match_count(player, 1) for player in self.players]
        player_scores = [self.get_player_score(player) for player in self.players]
        #print(player_scores)
        total_game_weeks = self.get_total_game_weeks(player_scores)
        #print(total_game_weeks)
        weighted_scores = self.weight_weeks(player_scores, total_game_weeks)
        #print(weighted_scores)

        total_weighted_score = sum(weighted_scores)
        #game_penalty = sum(abs(gc - 3) * 10 for gc in game_counts)

        team_count_penalty = self.get_team_count_penalty()

        #no_games = 0
        #for player in self.players:
       #     if player in self.team_handler.has_no_data:
        #        no_games += 100
        
        fitness_score = total_weighted_score - salary_penalty - games_penalty - team_count_penalty - position_penalty - duplication_penalty

        #print(f"\nFitness score: {fitness_score:.2f}, Salary: {self.salary}, "
        #    f"Weighted Scores: {weighted_scores}, Game Counts: {games_penalty}, "
        #    f"Team Count Penalty: {team_count_penalty}, Position Penalty: {position_penalty}")
        return fitness_score
    
    def print_fitness_breakdown(self, salary_cap = 100):
        salary_penalty = self.get_salary_penalty(salary_cap) #penality on salary
        #games_penalty = self.get_total_games_penalty() #penality on number of games played
        games_penalty = self.get_range_games_penalty(1, 6)

        position_penalty = self.get_invalid_position_penalty() 
        duplication_penalty = self.get_duplicate_players_penalty() #if player appears more than once in team

        #game_counts = [self.get_players_match_count(player, 1) for player in self.players]
        player_scores = [self.get_player_score(player) for player in self.players]
        total_game_weeks = self.get_total_game_weeks(player_scores)
        weighted_scores = self.weight_weeks(player_scores, total_game_weeks)

        total_weighted_score = sum(weighted_scores)
        #game_penalty = sum(abs(gc - 3) * 10 for gc in game_counts)

        team_count_penalty = self.get_team_count_penalty()

        #no_games = 0
        #for player in self.players:
       #     if player in self.team_handler.has_no_data:
        #        no_games += 100
        
        fitness_score = total_weighted_score - salary_penalty - games_penalty - team_count_penalty - position_penalty - duplication_penalty

        print(f"\nFitness score: {fitness_score:.2f}, Salary: {self.get_team_salary()}, "
            f"Weighted Scores: {sum(weighted_scores)}, Game Penalty: {games_penalty}, "
            f"Team Count Penalty: {team_count_penalty}, Position Penalty: {position_penalty}, Duplication Penalty: {duplication_penalty}, Salary Penalty: {salary_penalty}")

    def weight_weeks(self, player_scores, total_weeks):
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

    def get_total_game_weeks(self, player_scores):
        max_weeks = 0
        for player_data in player_scores:  
            if not player_data:
                continue  
            last_key = max(int(week) for week in player_data.keys())
            if last_key > max_weeks:
                max_weeks = last_key
        return max_weeks

    def get_player_score(self, player):
        stats = self.get_weekly_stats(player)
        filtered_weeks = {}
        for week, data in stats.items():
            if data['total_point'] != 0: 
                filtered_weeks[week] = data['total_point']
        
        return filtered_weeks if filtered_weeks else None
    
    def get_weekly_games_penalty(self, week):
        '''Calculate penalty based on number of games played in a week.'''
        total_penalty = 0
        for day in range(1, 8):
            active_players = self.get_max_active_players(week, day)
            total_penalty += max(0, 5 - len(active_players))

        return total_penalty
    
    def get_range_games_penalty(self, start_week, end_week):
        '''Calculate total games penalty across a range of weeks.'''
        total_penalty = 0
        for week in range(start_week, end_week + 1):
            total_penalty += self.get_weekly_games_penalty(week)
        return total_penalty
    
    def get_total_games_penalty(self):
        '''Calculate total games penalty across all weeks.'''
        return self.get_range_games_penalty(1, 26)
    
    def get_duplicate_players_penalty(self):
        '''Calculate penalty for duplicate players in the team.'''
        duplication_penalty = 0
        for player in self.players:
            apperances_on_teams = sum(1 for p in self.players if p.get("id") == player.get("id"))
            if apperances_on_teams > 1:
                duplication_penalty += 100
        return duplication_penalty
    
    def get_invalid_position_penalty(self):
        '''Calculate penalty for invalid player positions in the team.'''
        position_penalty = 0
        fc_count = sum(1 for p in self.players if p.get("position") == "fc")
        bc_count = sum(1 for p in self.players if p.get("position") == "bc")
        if fc_count != 5:
            position_penalty += abs(fc_count - 5) * 100
        if bc_count != 5:
            position_penalty += abs(bc_count - 5) * 100

        return position_penalty
    
    def get_salary_penalty(self, salary_cap):
        '''Calculate penalty based on team salary exceeding the cap.'''
        if self.get_team_salary() > salary_cap:
            return (self.get_team_salary() - salary_cap)  ** 2 * 500
        return 0
    
    def get_team_count_penalty(self):
        '''Calculate penalty for exceeding player count per team.'''
        if self.check_player_per_team() :
            return 0
        return 200
    
    def save_team(self, file_path="data/team_output.json"):
        '''Saves the team data to a specified JSON file.'''
        import json

        data = {
            "run" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fitness": self.calculate_fitness(),
            "salary": self.get_team_salary(),
            "players": [player.get("id") for player  in self.players]
        }
        with open(file_path, 'a', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            f.write('\n')


           