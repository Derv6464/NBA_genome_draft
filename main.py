import os
import json
from get_data import DataGenerator
from data_handler import DataHandler
from fitness import Fitness


def main():
    max_salary = 100
    data = DataGenerator("data")

    players, games = data.get_existing_data()

    handler = DataHandler(players, games, max_salary)
    fitness = Fitness(handler)
    team = handler.make_random_valid_team()
    total_games = 0
    for player in team:
        total_games += handler.get_players_match_count(player, 1)
        print(player.get("name"), player.get("position"), player.get("team"))

    fitness.evaluate_team(team)
    # for player in team:
    #     stats = fitness.get_player_score(player)
    #     print(f"Stats for {player.get('name')}: {stats}")

    print("team salary:", handler.get_team_salary(team))
    print("total games in week 1:", total_games)

    


if __name__ == "__main__":
    main()
