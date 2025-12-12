from runner import Runner
from analysis_tools.comparitor import Comparitor
from team import Team
from data_generator import DataGenerator


data_generator = DataGenerator("data")
players, teams, games = data_generator.get_existing_data()

runner = Runner(30, 1000, players, games, teams, 100, 7, ["Dervla", "Dominick", "Amy", "rank_1", "rank_2", "rank_3"])

five_teams = []

for i in range(5):
    team = runner.run_genetic_algorithm()
    five_teams.append(team)
    

avg_fitness = sum(team.fitness for team in five_teams) / len(five_teams)
avg_weekly_scores = [sum(team.get_week_score(week) for team in five_teams) / len(five_teams) for week in range(3,8)]
avg_days_scores = [sum(team.get_max_score(7, day) for team in five_teams) / len(five_teams) for day in range(1,8)]
print(f"Team Fitness: {team.fitness}")
print(f"Average Team Fitness: {avg_fitness}")
print(f"Average Weekly Scores (Weeks 3-7): {avg_weekly_scores}")

comp = runner.comparitor

weeks = list(range(3, 8))
fitness_table = {"Best Team": []}
for team_name in comp.comparison_teams.keys():
    fitness_table[team_name] = []
for week in weeks:
    comparison_fitness = comp.get_fitness_scores(week)
    fitness_table["Best Team"].append(avg_fitness)
    for team_name, score in comparison_fitness.items():
        fitness_table[team_name].append(score)

week_scores_table = {"Best Team": []}
for team_name in comp.comparison_teams.keys():
    week_scores_table[team_name] = []

for week in weeks:
    best_team_score = avg_weekly_scores[week - 3]
    week_scores_table["Best Team"].append(best_team_score)
    for team_name, teams in comp.comparison_teams.items():
        team_score = teams[week - 3].get_week_score(week)
        week_scores_table[team_name].append(team_score)

days = list(range(1, 8))
days_scores_table = {"Best Team": []}
for team_name in comp.comparison_teams.keys():
    days_scores_table[team_name] = []

for day in days:
    best_day_score = avg_days_scores[day - 1]
    days_scores_table["Best Team"].append(best_day_score)
    for team_name, teams in comp.comparison_teams.items():
        team_day_score = teams[7 - 3].get_max_score(7, day)
        days_scores_table[team_name].append(team_day_score)
    
    
runner.grapher.graph_hist_bar(
            x_data=fitness_table.keys(),
            y_data=fitness_table,
            category=weeks,
            cat_label="Week",
            y_label="Fitness Score",
            title="Fitness Comparison by Week (Histogram) (5 avg teams)"
    )

runner.grapher.graph_hist_bar(
            x_data=week_scores_table.keys(),
            y_data=week_scores_table,
            category=weeks,
            cat_label="Week",
            y_label="Weekly Score",
            title="Weekly Score Comparison by Week (Histogram) (5 avg teams)"
    )

runner.grapher.graph_hist_bar(
            x_data=days_scores_table.keys(),
            y_data=days_scores_table,
            category=days,
            cat_label="Day",
            y_label="Max Score",
            title=f"Max Possible Scores by Day – Week 7 (Histogram) (5 avg teams)"
    )   