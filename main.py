from data_generator import DataGenerator
from runner import Runner
import argparse

def main(week, episodes, population_size, max_salary, setup, ga, gp):
    print(f"Starting EA Program with Salary Cap: {max_salary}, Episodes: {episodes}, Population Size: {population_size} for week {week}")

    data_generator = DataGenerator("data")
    if setup:
        print("Setting up data from API...")
        print("Please don't touch anything while chrome is running...")
        data_generator.get_all_info(week)

    print("Loading player and game data...")

    players, teams, games = data_generator.get_existing_data()
    print(f"Loaded {len(players)} players, {len(teams)} teams, {len(games)} weeks of games\n")

    comp_temas = ["Dervla", "Dominick", "Amy", "rank_1", "rank_2", "rank_3"]
    
    runner = Runner(episodes, population_size, players, games, teams, max_salary, week, comp_temas)
    
    if ga:
        best_team = runner.run_genetic_algorithm()
        runner.run_algorithim_results(best_team)
    elif gp:
        best_fitness = runner.run_genetic_programming()
    elif ga and gp:
        pass
    else:
        raise ValueError("Either GA and/or GP must be true")


    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--week', type=int, default=7, help='Week number to generate team for') 
    parser.add_argument('-e', '--episodes', type=int, default=100, help='Number of generations to run')
    parser.add_argument('-p', '--population', type=int, default=10000, help='Population size for each generation')
    parser.add_argument('-s', '--salary', type=int, default=100, help='Maximum salary cap for the team')
    parser.add_argument('--setup', action='store_true', help='Whether to setup data from API')
    parser.add_argument('--ga', action='store_true', help='Run Genetic Algorithm')
    parser.add_argument('--gp', action='store_true', help='Run Genetic Programming')
    args = parser.parse_args()
    main(args.week, args.episodes, args.population, args.salary, args.setup, args.ga, args.gp)
