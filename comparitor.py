import json
from team import Team
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

class Comparitor:
    def __init__(self, team_handler, comparison_teams_names, start_week=3, end_week=6):
        self.team_handler = team_handler
        self.comparison_teams = dict()
        self.start_week = start_week
        self.end_week = end_week

        for team in comparison_teams_names:
            self.comparison_teams[team] = self.make_comparison_teams(team)

    def read_comparion_file(self, file_path="data"):
        with open(f"{file_path}/comparison_teams.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
        
    def make_comparison_teams(self, team_name) -> list[Team]:
        teams_data = self.read_comparion_file().get(team_name)
        teams = []
        for week_num in range(self.start_week, self.end_week + 1):
            teams.append(self.team_handler.make_team_from_ids(teams_data[str(week_num)]))

        return teams

    def get_fitness_scores(self, week):
        fitness = dict()
        for team_name, teams in self.comparison_teams.items():
            team = teams[week - 3]
            score = team.fitness
            fitness[team_name] = score

        return fitness
    
    def print_table(self,table_dict, weeks, label):
        rows = []
        header = [label] + [str(w) for w in weeks]
        rows.append(header)

        for team_name, values in table_dict.items():
            rows.append([team_name] + [str(v) for v in values])


        col_widths = [max(len(row[col]) for row in rows) for col in range(len(rows[0]))]

        for row in rows:
            padded = [row[i].ljust(col_widths[i]) for i in range(len(row))]
            print(" | ".join(padded))
    
    def compare_fitness(self, best_team):
        weeks = list(range(self.start_week, self.end_week + 1))


        table = {"Best Team": []}
        for team_name in self.comparison_teams.keys():
            table[team_name] = []

        table["Winning Team"] = []

        for week in weeks:
            comparison_fitness = self.get_fitness_scores(week)

            table["Best Team"].append(best_team.fitness)

            for team_name, score in comparison_fitness.items():
                table[team_name].append(score)

            if best_team.fitness >= max(self.get_fitness_scores(week).values()):
                winning_team = "Best Team"
            else:
                winning_team = max(self.get_fitness_scores(week), key=self.get_fitness_scores(week).get)

            table["Winning Team"].append(winning_team)

        self.fitness_table = table
        print("\n=== Fitness Comparison Table ===")
        self.print_table(table, weeks, "week")

    def compare_weekly_scores(self, best_team):
        weeks = list(range(self.start_week, self.end_week + 1))

        table = {"Best Team": []}
        for team_name in self.comparison_teams.keys():
            table[team_name] = []
        table["Winning Team"] = []

        for week in weeks:
            best_team_score = best_team.get_week_score(week)
            table["Best Team"].append(best_team_score)

            for team_name, teams in self.comparison_teams.items():
                team_score = teams[week - 3].get_week_score(week)
                table[team_name].append(team_score)

            
            if best_team_score >= max(teams[week - 3].get_week_score(week) for teams in self.comparison_teams.values()):
                winning_team = "Best Team"
            else:
                winning_team = max(self.comparison_teams.items(), key=lambda item: item[1][week - 3].get_week_score(week))[0]
            table["Winning Team"].append(winning_team)

        self.weekly_score_table = table
        print("\n=== Weekly Score Comparison Table ===")
        self.print_table(table, weeks, "week")

    def compare_days_scores(self, best_team, weeks, days):
        for week in weeks:
            table = {"Best Team": []}
            for team_name in self.comparison_teams.keys():
                table[team_name] = []

            table["Winning Team"] = []
            print(f"\n=== Week {week} Max Possible Scores Table ===")
            for day in days:
                best_team_score = best_team.get_max_score(week, day)
                table["Best Team"].append(best_team_score)

                for team_name, teams in self.comparison_teams.items():
                    team_score = teams[week - 3].get_max_score(week, day)
                    table[team_name].append(team_score)
                if best_team_score >= max(teams[week - 3].get_max_score(week, day) for teams in self.comparison_teams.values()):
                    winning_team = "Best Team"
                else:
                    winning_team = max(self.comparison_teams.items(), key=lambda item: item[1][week - 3].get_max_score(week, day))[0]
                table["Winning Team"].append(winning_team)

            self.print_table(table, days, "day")

                
            
    def graph_fitness(self):
        weeks = list(range(self.start_week, self.end_week + 1))
        teams = [team for team in self.fitness_table.keys() if team != "Winning Team"]

        # width of each bar inside a week
        bar_width = 0.8 / len(teams)

        # positions of each week on x-axis
        x = np.arange(len(weeks))

        plt.figure()

        for i, team_name in enumerate(teams):
            scores = self.fitness_table[team_name]
            plt.bar(x + i * bar_width, scores, width=bar_width, label=team_name)

        plt.xlabel("Week")
        plt.ylabel("Fitness")
        plt.title("Fitness Comparison by Week (Histogram)")
        plt.xticks(x + bar_width * (len(teams)-1) / 2, weeks)
        plt.legend()
        file_path = os.path.join("data/images/", f"{datetime.now()}-2.png")
        plt.savefig(file_path, bbox_inches='tight')

    def graph_weekly_scores(self):
        weeks = list(range(self.start_week, self.end_week + 1))
        teams = [team for team in self.weekly_score_table.keys() if team != "Winning Team"]

        bar_width = 0.8 / len(teams)
        x = np.arange(len(weeks))

        plt.figure()

        for i, team_name in enumerate(teams):
            scores = self.weekly_score_table[team_name]
            plt.bar(x + i * bar_width, scores, width=bar_width, label=team_name)

        plt.xlabel("Week")
        plt.ylabel("Weekly Score")
        plt.title("Weekly Score Comparison by Week (Histogram)")
        plt.xticks(x + bar_width * (len(teams)-1) / 2, weeks)
        plt.legend()
        file_path = os.path.join("data/images/", f"{datetime.now()}-2.png")
        plt.savefig(file_path, bbox_inches='tight')

    def graph_days_scores(self, best_team, weeks, days):

        for week in weeks:
            table = {"Best Team": []}
            for team_name in self.comparison_teams.keys():
                table[team_name] = []

            for day in days:
                best_team_score = best_team.get_max_score(week, day)
                table["Best Team"].append(best_team_score)

                for team_name, teams in self.comparison_teams.items():
                    team_score = teams[week - 3].get_max_score(week, day)
                    table[team_name].append(team_score)


        teams = list(table.keys())
        bar_width = 0.8 / len(teams)
        x = np.arange(len(days))

        plt.figure()

        for i, team_name in enumerate(teams):
            scores = table[team_name]
            plt.bar(x + i * bar_width, scores, width=bar_width, label=team_name)

        plt.xlabel("Day")
        plt.ylabel("Max Score")
        plt.title(f"Max Possible Scores by Day – Week {week}")
        plt.xticks(x + bar_width * (len(teams) - 1) / 2, days)
        plt.legend()
        file_path = os.path.join("data/images/", f"{datetime.now()}-4.png")
        plt.savefig(file_path, bbox_inches='tight')

