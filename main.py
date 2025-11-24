import os
import json
from get_data import DataGenerator
from data_handler import DataHandler



def main():
    max_salary = 22
    data = DataGenerator("data")

    data.get_existing_data()
  

    handler = DataHandler(data.players, data.teams, max_salary)

    team = (handler.make_random_team())
    for player in team:
        print(player.get("name"), player.get("position"), player.get("team"))

    print("team salary:", handler.get_team_salary(team))


if __name__ == "__main__":
    main()
