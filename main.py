from data_generator import DataGenerator
from team_handler import TeamHandler
from population import Population
from genetic_operators import GeneticOperators
from team import Team
from schedule import Schedule
from comparitor import Comparitor

import random
import matplotlib.pyplot as plt
from datetime import datetime
import os
import argparse

def print_team(team: Team):
    print(f"fitness: {team.calculate_fitness()}")
    print(f"Cost: {team.get_team_salary()}")
    print(f"is valid {team.check_team_validity()} (Salary Cap: {team.check_player_salary()}, Position Cap: {team.check_player_position()}, Team Cap: {team.check_player_per_team()})")
    for player in team.players:
        print(f"{player.get('name')} - {player.get('team')} - {player.get('position')} - Salary: {player.get('salary')} - Total Points: {player.get('total_points')}")

def main(week, episodes, population_size, max_salary):
    print(f"Starting Genetic Algorithm with Salary Cap: {max_salary}, Episodes: {episodes}, Population Size: {population_size} for week {week}")
    max_salary = max_salary
    episodes = episodes
    population_size = population_size
    elitism_count = int(population_size * 0.001)
    generate_team_for_week = week

    #loading in player & game data
    data_generator = DataGenerator("data")
    #data_generator.get_game_data()
    #data_generator.update_player_stats() # Uncomment to update player stats from API
    
    players, teams, games = data_generator.get_existing_data()

    sch = Schedule(games)
    team_handler = TeamHandler(players, sch, max_salary, generate_team_for_week)
    genetic_ops = GeneticOperators(players)
    population = Population()
    comparitor = Comparitor(team_handler, ["Dervla", "Dominick", "Amy", "rank_1", "rank_2", "rank_3"], 3, 7)

    #depths = [team_handler.get_best_players, team_handler.get_random_no_caps, team_handler.get_random_position_cap, team_handler.get_random_team_cap, team_handler.get_random_salary_cap]
    #individuals = population.ramped_half_and_half(50, depths, team_handler.make_random_valid_team)

    individuals = [team_handler.make_random_valid_team() for _ in range(population_size)]

    generation_stats = []
    total_timer = datetime.now()
    counter = 0
    while counter < episodes:
        ep_timer = datetime.now()
        individuals.sort(key=lambda team: team.fitness, reverse=True)
        generation_stats.append({
            "generation": counter,
            "best_fitness": individuals[0].fitness,
            "average_fitness": sum(team.fitness for team in individuals) / len(individuals),
            "worst_fitness": individuals[-1].fitness
        })

        print(f"\n=== Generation {counter} ===")
        print(f"Best fitness: {individuals[0].fitness}")
        print(f"Average fitness: {sum(team.fitness for team in individuals) / len(individuals)}")
        print(f"Worst fitness: {individuals[-1].fitness}")

        next_generation = [team.copy() for team in individuals[:elitism_count]]
        wheel = population.make_wheel(individuals)

        while len(next_generation) < len(individuals):
            parent1 = population.selector(wheel)
            parent2 = population.selector(wheel)

            random.shuffle(parent1.players)
            random.shuffle(parent2.players)

            child1, child2 = genetic_ops.crossover(parent1.copy(), parent2.copy())
            child1.re_evaluate()
            child2.re_evaluate()
            next_generation.append(child1)
            next_generation.append(child2)

        for i in range(elitism_count, len(next_generation)):
            if random.random() < 0.2:
                genetic_ops.mutate(next_generation[i].players)
                next_generation[i].re_evaluate()

        individuals = next_generation
        counter += 1
        print(f"Generation {counter} completed in {datetime.now() - ep_timer}")

    print(f"\nTotal Time Taken: {datetime.now() - total_timer}")
    best_team = max(individuals, key=lambda team: team.fitness)

    print("\n=== Final Best Team ===")
    print_team(best_team)

    comparitor.compare_fitness(best_team)
    comparitor.compare_weekly_scores(best_team)
    comparitor.compare_days_scores(best_team, [6], [1,2,3,4,5,6,7])

    best_team.save_team()
   
    plt.plot([stat["generation"] for stat in generation_stats], [stat["best_fitness"] for stat in generation_stats], label="Best Fitness")
    plt.plot([stat["generation"] for stat in generation_stats], [stat["average_fitness"] for stat in generation_stats], label="Average Fitness")
    plt.plot([stat["generation"] for stat in generation_stats], [stat["worst_fitness"] for stat in generation_stats], label="Worst Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Fitness over Generations")
    plt.legend()
    file_path = os.path.join("data/images/", f"{datetime.now()}-1.png")
    plt.savefig(file_path, bbox_inches='tight')

    comparitor.graph_fitness()
    comparitor.graph_weekly_scores()
    comparitor.graph_days_scores(best_team, [generate_team_for_week], [1,2,3,4,5,6,7])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--week', type=int, default=7, help='Week number to generate team for') 
    parser.add_argument('-e', '--episodes', type=int, default=100, help='Number of generations to run')
    parser.add_argument('-p', '--population', type=int, default=10000, help='Population size for each generation')
    parser.add_argument('-s', '--salary', type=int, default=100, help='Maximum salary cap for the team')
    args = parser.parse_args()
    main(args.week, args.episodes, args.population, args.salary)
