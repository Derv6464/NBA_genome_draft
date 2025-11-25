import data_handler

class Fitness:
    def __init__(self, data_handler):
        self.data_handler = data_handler
        
    def evaluate_team(self, team):
        if not self.data_handler.check_team_validity(team):
            return float('inf')

        total_salary = self.data_handler.get_team_salary(team)
        game_counts = [self.data_handler.get_players_match_count(player, 1) for player in team]
        player_scores = [self.get_player_score(player) for player in team]
        total_game_weeks = self.get_total_game_weeks(player_scores)
        weighted_scores = self.weight_weeks(player_scores, total_game_weeks)

        salary_cap = self.data_handler.max_salary
        salary_penalty = 0
        if total_salary > salary_cap:
            salary_penalty = (total_salary - salary_cap) * 100
        total_weighted_score = sum(weighted_scores)
        game_penalty = sum(abs(gc - 3) * 10 for gc in game_counts)

        fitness_score = total_weighted_score - salary_penalty - game_penalty

        print(f"\nFitness score: {fitness_score:.2f}, Salary: {total_salary}, "
            f"Weighted Scores: {weighted_scores}, Game Counts: {game_counts}")
        return fitness_score

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
        stats = self.data_handler.get_weekly_stats(player)
        filtered_weeks = {}
        for week, data in stats.items():
            if data.get('per_game'): 
                filtered_weeks[week] = data['total_point']
        
        return filtered_weeks if filtered_weeks else None

