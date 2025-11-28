import os
import json
from get_data import DataGenerator
from data_handler import DataHandler
from fitness import Fitness
from genetic_operators import GeneticOperators


def main():
    max_salary = 100
    data = DataGenerator("data")

    players, games = data.get_existing_data()

    handler = DataHandler(players, games, max_salary)
    fitness = Fitness(handler)
    genetic_ops = GeneticOperators(handler, players)
    team = handler.make_random_valid_team()
    team2 = handler.make_random_valid_team()
    total_games = 0
    # for player in team:
    #     total_games += handler.get_players_match_count(player, 1)
    #     print(player.get("name"), player.get("position"), player.get("team"))

    print("----- Team 1 -----")
    for player in team:
        print(player.get("name"))
    
    print("----- Team 2 -----")
    for player in team2:
        print(player.get("name"))

    fitness.evaluate_team(team)
    fitness.evaluate_team(team2)
    genetic_ops.mutate(team)
    genetic_ops.crossover(team, team2)
    fitness.evaluate_team(team)
    fitness.evaluate_team(team2)

    print("----- Team 1 -----")
    for player in team:
        print(player.get("name"))
    
    print("----- Team 2 -----")
    for player in team2:
        print(player.get("name"))


    print("team salary:", handler.get_team_salary(team))
    print("total games in week 1:", total_games)

if __name__ == "__main__":
    main()
