from data_generator import DataGenerator
from runner import Runner

import random

import os
import argparse


def main(week, episodes, population_size, max_salary, setup, rounds, ga, gp):
    print(f"Starting Genetic Algorithm with Salary Cap: {max_salary}, Episodes: {episodes}, Population Size: {population_size} for week {week}")
    max_salary = max_salary
    episodes = episodes
    population_size = population_size
    elitism_count = int(population_size * 0.001)
    generate_team_for_week = week

    data_generator = DataGenerator("data")
    if setup:
        print("Setting up data from API...")
        print("Please don't touch anything while chrome is running...")
        data_generator.get_all_info(week)
    #loading in player & game dats
    print("Loading player and game data...")
   
    #data_generator.get_game_data()
    #data_generator.update_player_stats() # Uncomment to update player stats from API
    
    players, teams, games = data_generator.get_existing_data()
    print(f"Loaded {len(players)} players, {len(teams)} teams, {len(games)} games\n")

    comp_temas = ["Dervla", "Dominick", "Amy", "rank_1", "rank_2", "rank_3"]
    

    #depths = [team_handler.get_best_players, team_handler.get_random_no_caps, team_handler.get_random_position_cap, team_handler.get_random_team_cap, team_handler.get_random_salary_cap]
    #individuals = population.ramped_half_and_half(50, depths, team_handler.make_random_valid_team)
    runner = Runner(episodes, population_size, players, games, teams, max_salary, generate_team_for_week, comp_temas)
    
    if ga:
        best_team = runner.run_genetic_algorithm()
    elif gp:
        best_fitness = runner.run_programing_results()
    elif ga and gp:
        best_fitness = runner.run_programing_results()
        best_team = runner.run_genetic_programming(episodes, players, games, runner.genertic_ops)
    else:
        raise ValueError("Either GA and/or GP must be true")


    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--week', type=int, default=7, help='Week number to generate team for') 
    parser.add_argument('-e', '--episodes', type=int, default=100, help='Number of generations to run')
    parser.add_argument('-p', '--population', type=int, default=10000, help='Population size for each generation')
    parser.add_argument('-s', '--salary', type=int, default=100, help='Maximum salary cap for the team')
    parser.add_argument('--setup', action='store_true', help='Whether to setup data from API')
    args = parser.parse_args()
    main(args.week, args.episodes, args.population, args.salary, args.setup, rounds=0)
