import os
import json
from get_data import DataGenerator
from data_handler import DataHandler



def main():
    data = DataGenerator("data")
    data.get_existing_data()
  

    handler = DataHandler(data.players, data.teams)

    team = (handler.make_random_team())
    for player in team:
        print(player["name"])




if __name__ == "__main__":
    main()
