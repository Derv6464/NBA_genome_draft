from data_generator import DataGenerator
from team_handler import TeamHandler
from population import Population
from fitness import Fitness
from genetic_operators import GeneticOperators
from team import Team
from schedule import Schedule

import random
import json

def print_team(team):
    print(f"fitness: {team.calculate_fitness()}")
    print(f"Cost: {team.get_team_salary()}")
    print(f"is valid {team.check_team_validity()}")
    for player in team.players:
        print(f"{player.get('name')} - {player.get('team')} - {player.get('position')} - Salary: {player.get('salary')} - Total Points: {player.get('total_points')}")
    team.print_fitness_breakdown()

def read_comparion_file(file_path="data"):
     with open(f"{file_path}/comparison_teams.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

def main():
    max_salary = 100
    episodes = 50

    #loading in player & game data
    data_generator = DataGenerator("data")
    players, teams, games = data_generator.get_existing_data()

    sch = Schedule(games)
    team_handler = TeamHandler(players, sch, max_salary)
    #fitness = Fitness(team_handler)
    genetic_ops = GeneticOperators(players)
    population = Population()

    depths = [team_handler.get_best_players, team_handler.get_random_no_caps, team_handler.get_random_position_cap, team_handler.get_random_team_cap, team_handler.get_random_salary_cap]
    
    individuals = population.ramped_half_and_half(2000, depths, team_handler.make_random_valid_team)
    random_wheel = population.make_wheel()
    
    counter = 0
    while counter < episodes:
        individuals.sort(key=lambda team: team.calculate_fitness(), reverse=True)

        print(f"\n=== Generation {counter} ===")
        print(f"Best fitness: {individuals[0].calculate_fitness()}")

        next_generation = individuals[:len(individuals)//2]

        while len(next_generation) < len(individuals):
            parent1 = random.choice(individuals[:5])
            parent2 = random.choice(individuals[:5])
            child1, child2 = genetic_ops.crossover(parent1.copy(), parent2.copy())
            next_generation.append(child1)
            next_generation.append(child2)

        for i in range(len(next_generation)):
            if random.random() < 0.2:
                genetic_ops.mutate(next_generation[i].players)

        individuals = next_generation
        counter += 1

    best_team = max(individuals, key=lambda team: team.calculate_fitness())

    print("\n=== Final Best Team ===")
    print_team(best_team)

    #bestTeam = Team(best_team, sch)

    dervlas_teams_data = read_comparion_file().get("Dervla")
    dervlas_teams_ids = []
    for week_num in range(3, 7):
        dervlas_teams_ids.append(team_handler.make_team_from_ids(dervlas_teams_data[str(week_num)]))

    domicks_teams_data = read_comparion_file().get("Dominick")
    domicks_teams_ids = []
    for week_num in range(3, 7):
        domicks_teams_ids.append(team_handler.make_team_from_ids(domicks_teams_data[str(week_num)]))

    week_scores = best_team.get_weeks_scores()

    print()

    dervlas_scores = [0 for _ in range(26)]
    for i, team in enumerate(dervlas_teams_ids, start=3):
        score = team.get_week_score(i)
        print("Dervla week ", i, " fitness: ", team.calculate_fitness())
        dervlas_scores[i-1] = score

    print()
    domincks_scores = [0 for _ in range(26)]
    for i, team in enumerate(domicks_teams_ids, start=3):
        score = team.get_week_score(i)
        print("Domick week ", i, " fitness: ", team.calculate_fitness())
        domincks_scores[i-1] = score

    print()
    print("best: ", week_scores)
    print("dervla: ",dervlas_scores)
    print("domick: ", domincks_scores)

    best_team.save_team()

if __name__ == "__main__":
    main()
