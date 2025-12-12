import json
from team import Team
from analysis_tools.grapher import Grapher
from team_handler import TeamHandler

class Comparitor:
    def __init__(self, team_handler:TeamHandler, comparison_teams_names:list[str], grapher:Grapher, start_week=3, end_week=6):
        self.team_handler = team_handler
        self.comparison_teams = dict()
        self.start_week = start_week
        self.end_week = end_week
        self.grapher = grapher

        for team in comparison_teams_names:
            self.comparison_teams[team] = self.make_comparison_teams(team)

    def read_comparion_file(self, file_path="data") -> dict:
        with open(f"{file_path}/comparison_teams.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
        
    def make_comparison_teams(self, team_name) -> list[Team]:
        teams_data = self.read_comparion_file().get(team_name)
        teams = []
        for week_num in range(self.start_week, self.end_week + 1):
            teams.append(self.team_handler.make_team_from_ids(teams_data[str(week_num)]))

        return teams

    def get_fitness_scores(self, week:int) -> dict:
        fitness = dict()
        for team_name, teams in self.comparison_teams.items():
            team = teams[week - 3]
            score = team.fitness
            fitness[team_name] = score

        return fitness
    
    def _print_table(self,table_dict: dict, weeks : list, label):
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
        self._print_table(table, weeks, "week")

    def compare_weekly_scores(self, best_team: Team):
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
        self._print_table(table, weeks, "week")

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

            self._print_table(table, days, "day")

    def graph_fitness(self):
        weeks = list(range(self.start_week, self.end_week + 1))
        teams = [team for team in self.fitness_table.keys() if team != "Winning Team"]

        self.grapher.graph_hist_bar(
            x_data=teams,
            y_data=self.fitness_table,
            category=weeks,
            cat_label="Week",
            y_label="Fitness Score",
            title="Fitness Comparison by Week (Histogram)"
        )

    def graph_weekly_scores(self):
        weeks = list(range(self.start_week, self.end_week + 1))
        teams = [team for team in self.weekly_score_table.keys() if team != "Winning Team"]

        self.grapher.graph_hist_bar(
            x_data=teams,
            y_data=self.weekly_score_table,
            category=weeks,
            cat_label="Week",
            y_label="Weekly Score",
            title="Weekly Score Comparison by Week (Histogram)"
        )

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

        self.grapher.graph_hist_bar(
            x_data=list(table.keys()),
            y_data=table,
            category=days,
            cat_label="Day",
            y_label="Max Score",
            title=f"Max Possible Scores by Day – Week {week} (Histogram)"
        )