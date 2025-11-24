import os
import json
from get_data import DataGenerator
from data_handler import DataHandler

#to do
#- making team player 2
#- fc, bc
#


def main():
    max_salary = 100
    data = DataGenerator("data")

    data.update_player_stats()

    handler = DataHandler(data.players, data.teams, max_salary)

    team = (handler.make_random_valid_team())
    
    for player in team:
        print(player.get("name"), player.get("position"), player.get("team"))

    print("team salary:", handler.get_team_salary(team))


if __name__ == "__main__":
    main()
