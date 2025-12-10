import json
from copy import deepcopy
class Tree:
    def __init__(self, root, sch, fitness):
        self.root = root
        self.fitness = fitness
        self.sch = sch

    def copy(self):
        return Tree(deepcopy(self.root), self.sch, self.fitness)

    def to_string(self):
        def inorder_traversal(node):
            if node is None:
                return ""
            if node.is_leaf():
                return str(node.value)
            left_str = inorder_traversal(node.left)
            right_str = inorder_traversal(node.right)
            return f"({left_str} {node.value} {right_str})"
        return inorder_traversal(self.root)
    
    def get_gp_ranking_data(self):
        with open("data/gp_data.json", "r") as f:
            data = json.load(f)
        return data
    
    def get_team_features(self, players, target_week=None):
        salary = sum(float(p.get("salary", 0)) for p in players)
        total_points = sum(float(p.get("total_points", 0)) for p in players)
        fc_count = sum(1 for p in players if p.get("position") == "fc")
        bc_count = sum(1 for p in players if p.get("position") == "bc")

        salary_cap = 100
        salary_penalty = 0
        if salary > salary_cap:
            salary_penalty = (salary - salary_cap) ** 2 * 500

        position_penalty = 0
        if fc_count != 5:
            position_penalty += abs(fc_count - 5) * 100
        if bc_count != 5:
            position_penalty += abs(bc_count - 5) * 100

        team_count_penalty = 0
        team_counts = {}
        for p in players:
            t = p.get("team")
            if t:
                team_counts[t] = team_counts.get(t, 0) + 1
        if any(c > 2 for c in team_counts.values()):
            team_count_penalty = 200

        weekly_scores = {}
        max_week = 0


        total_rebounds = total_assists = total_steals = total_blocks = 0
        games_count = 0

        for p in players:
            weekly = p.get("weekly_stats", {})

            if target_week is not None:
                week_key = str(int(target_week))
                if week_key in weekly:
                    week_data = weekly[week_key]
                    max_week = max(max_week, int(week_key))
                    score = week_data.get("total_point", 0)
                    if score:
                        weekly_scores[week_key] = weekly_scores.get(week_key, 0) + score
                    for day_stats in week_data.get("game_stats", {}).values():
                        for game in day_stats:
                            if len(game) >= 11:
                                total_rebounds += int(game[7])
                                total_assists += int(game[8])
                                total_blocks += int(game[9])
                                total_steals += int(game[10])
                                games_count += 1
                continue

            for week_str, week_data in weekly.items():
                week = int(week_str)
                max_week = max(max_week, week)
                score = week_data.get("total_point", 0)
                if score:
                    weekly_scores[week_str] = weekly_scores.get(week_str, 0) + score
                for day_stats in week_data.get("game_stats", {}).values():
                    for game in day_stats:
                        if len(game) >= 11:
                            total_rebounds += int(game[7])
                            total_assists += int(game[8])
                            total_blocks += int(game[9])
                            total_steals += int(game[10])
                            games_count += 1

        weighted_score = 0
        if max_week > 0:
            for week_str, score in weekly_scores.items():
                if target_week is not None:
                    weight = 1.0
                else:
                    week = int(week_str)
                    weight = week / max_week
                weighted_score += score * weight

        avg_weekly_score = (
            sum(weekly_scores.values()) / len(weekly_scores)
            if weekly_scores else
            0
        )

        eps = 1e-6
        norm = {
            "salary": salary / 100.0,
            "points": total_points / 1000.0,
            "rebounds": total_rebounds / 100.0,
            "assists": total_assists / 100.0,
            "blocks": total_blocks / 100.0,
            "steals": total_steals / 100.0,
            "fc_count": fc_count / 5.0,
            "bc_count": bc_count / 5.0,
            "weighted_score": weighted_score / 5000.0,
            "salary_penalty": salary_penalty / 10000.0,
            "position_penalty": position_penalty / 1000.0,
            "team_count_penalty": team_count_penalty / 1000.0,
            "avg_weekly_score": avg_weekly_score / 1000.0,
            "total_weeks": (1.0 if target_week is not None else max_week) / 26.0,
            "games_count": games_count / 40.0,
        }
        norm["points_per_salary"] = (norm["avg_weekly_score"]) / (norm["salary"] + eps)

        return norm


    def calculate_fitness(self, data_points, schedule=None):


        weeks_data = self.get_gp_ranking_data()
        try:
            with open("data/messed_up_name.json", "r", encoding="utf-8") as f:
                messed = json.load(f).get("players", {})
        except Exception:
            messed = {}
        
        all_ranking_errors = []


        for week_name, week_info in weeks_data.items():
            rankings = week_info["rankings"]
            
            if not rankings:
                continue
            
            teams_with_scores = []
            
            for team_entry in rankings:
                actual_place = team_entry["place"]
                player_names = team_entry["players"]
                try:
                    week_num = int(str(week_name).split('_')[1])
                except Exception:
                    week_num = None
                
                players = []
                for name in player_names:
                    player = next((p for p in data_points if p.get("name") == name), None)
                    if not player:
                        fixed = messed.get(name)
                        if fixed:
                            player = next((p for p in data_points if p.get("name") == fixed), None)
                    if not player:
                        norm = name.replace(".", "").replace("-", " ").replace("'", "'")
                        norm = " ".join(norm.split())
                        player = next((p for p in data_points if p.get("name") == norm), None)
                    if player:
                        players.append(player)
                    else:
                        print(f"Error: Could not find player '{name}' (fixed: '{messed.get(name, '')}') in data_points")
                        exit()
                
                features = self.get_team_features(players, target_week=week_num)
                
                predicted_fitness = self.root.evaluate(features)

                fc_count_dbg = sum(1 for p in players if p.get("position") == "fc")
                bc_count_dbg = sum(1 for p in players if p.get("position") == "bc")
                if fc_count_dbg != 5 or bc_count_dbg != 5:
                    pos_list = [p.get("position") for p in players]
                    print(f"[PosDebug] {week_name} | fc={fc_count_dbg} bc={bc_count_dbg} | positions={pos_list} | team={', '.join(player_names)}...")

                is_valid = True
                
                teams_with_scores.append({
                    'actual_place': actual_place,
                    'predicted_fitness': predicted_fitness
                })
            
            teams_with_scores.sort(key=lambda x: x['predicted_fitness'], reverse=True)
            
            predicted_fitness_values = [t['predicted_fitness'] for t in teams_with_scores]
            unique_values = len(set(predicted_fitness_values))
            
            if unique_values == 1:
                all_ranking_errors.append(10.0)
                continue
            
            for i, team in enumerate(teams_with_scores):
                team['predicted_place'] = i + 1
            
            actual_places = [t['actual_place'] for t in teams_with_scores]
            predicted_places = [t['predicted_place'] for t in teams_with_scores]
            
            n = len(actual_places)
            concordant = 0
            discordant = 0
            
            for i in range(n):
                for j in range(i + 1, n):
                    actual_diff = actual_places[i] - actual_places[j]
                    predicted_diff = predicted_places[i] - predicted_places[j]
                    
                    if (actual_diff > 0 and predicted_diff > 0) or (actual_diff < 0 and predicted_diff < 0):
                        concordant += 1
                    elif (actual_diff > 0 and predicted_diff < 0) or (actual_diff < 0 and predicted_diff > 0):
                        discordant += 1
            
            total_pairs = n * (n - 1) / 2
            tau = (concordant - discordant) / total_pairs if total_pairs > 0 else 0
            
            error = 1.0 - tau
            
            diversity_ratio = unique_values / len(predicted_fitness_values)
            if diversity_ratio < 0.5:
                error += (1.0 - diversity_ratio) * 2.0
            
            all_ranking_errors.append(error)
        
        avg_error = sum(all_ranking_errors) / len(all_ranking_errors) if all_ranking_errors else float('inf')

        def _count_nodes(node):
            if node is None:
                return 0
            return 1 + _count_nodes(node.left) + _count_nodes(node.right)

        node_count = _count_nodes(self.root)
        size_penalty = 0.001 * node_count

        if node_count <= 1:
            size_penalty += 5.0

        self.fitness = avg_error + size_penalty
        return self.fitness


       
        
        
