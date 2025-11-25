import os
import json
from get_data import DataGenerator
from data_handler import DataHandler
from population import Population


def main():
    max_salary = 100
    data = DataGenerator("data")

    players, games = data.get_existing_data()

    handler = DataHandler(players, games, max_salary)

    team = handler.get_best_players()
    depths = [handler.get_best_players, handler.get_random_no_caps, handler.get_random_position_cap, handler.get_random_team_cap, handler.get_random_salary_cap]

    pop = Population()

    individuals = pop.ramped_half_and_half(50, depths, handler.make_random_valid_team)
    team = individuals[0]

    valid = 0
    invalid = 0

    for team in individuals:
        #for player in team:
        #    print(player.get("name"), end=", ")
        if handler.check_team_validity(team):
            valid += 1
        else:
            invalid += 1

    print(f"Valid teams: {valid}, Invalid teams: {invalid}")

if __name__ == "__main__":
    main()
