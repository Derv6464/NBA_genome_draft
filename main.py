from data_generator import DataGenerator
from team_handler import TeamHandler
from population import Population
from fitness import Fitness
from genetic_operators import GeneticOperators
from team import Team
from schedule import Schedule

import random
import json
import matplotlib.pyplot as plt
from datetime import datetime

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
    #data_generator.update_player_stats()
    
    players, teams, games = data_generator.get_existing_data()

    sch = Schedule(games)
    team_handler = TeamHandler(players, sch, max_salary)
    #fitness = Fitness(team_handler)
    genetic_ops = GeneticOperators(players)
    population = Population()

    depths = [team_handler.get_best_players, team_handler.get_random_no_caps, team_handler.get_random_position_cap, team_handler.get_random_team_cap, team_handler.get_random_salary_cap]
    
    individuals = population.ramped_half_and_half(5000, depths, team_handler.make_random_valid_team)
    random_wheel = population.make_wheel(individuals)
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
        #individuals[0].print_fitness_breakdown()

        next_generation = individuals[:len(individuals)//2]

        while len(next_generation) < len(individuals):
            parent1 = random.choice(individuals[:5])
            parent2 = random.choice(individuals[:5])
            child1, child2 = genetic_ops.crossover(parent1.copy(), parent2.copy())
            child1.re_evaluate()
            child2.re_evaluate()
            next_generation.append(child1)
            next_generation.append(child2)

        for i in range(len(next_generation)):
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

    for week in range(3, 7):
        dervla_total = 0
        domick_total = 0
        best_total = 0
        print(f"\n=== Week {week} Comparison ===")
        for day in range(1, 7):
            dervla_total += dervlas_teams_ids[week-3].get_max_score(week,day)
            domick_total += domicks_teams_ids[week-3].get_max_score(week,day)
            best_total += best_team.get_max_score(week,day)
 
        print(f"\nDervla's total week {week} score: {dervla_total}")
        print(f"Domick's total week {week} score: {domick_total}")
        print(f"Best total week {week} score: {best_total}")

    best_team.save_team()
    #print(generation_stats)
    plt.plot([stat["generation"] for stat in generation_stats], [stat["best_fitness"] for stat in generation_stats], label="Best Fitness")
    plt.plot([stat["generation"] for stat in generation_stats], [stat["average_fitness"] for stat in generation_stats], label="Average Fitness")
    plt.plot([stat["generation"] for stat in generation_stats], [stat["worst_fitness"] for stat in generation_stats], label="Worst Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Fitness over Generations")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
