from data_generator import DataGenerator
from team_handler import TeamHandler
from population import Population
from genetic_operators import GeneticOperators
from team import Team
from schedule import Schedule
from tree.tree import Tree

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

    print("=== Starting NBA GP Fitness Evolution ===\n")
    
    #loading in player & game data
    print("Loading player and game data...")
    data_generator = DataGenerator("data")
    #data_generator.update_player_stats()
    
    players, teams, games = data_generator.get_existing_data()
    print(f"Loaded {len(players)} players, {len(teams)} teams, {len(games)} games\n")

    sch = Schedule(games)
    team_handler = TeamHandler(players, sch, max_salary)
    #fitness = Fitness(team_handler)
    genetic_ops = GeneticOperators(players)
    population = Population()

    depths = [team_handler.get_best_players, team_handler.get_random_no_caps, team_handler.get_random_position_cap, team_handler.get_random_team_cap, team_handler.get_random_salary_cap]
    
    fitness_individuals = population.ramped_half_and_half(size=1000, grow_funcs=5, type="fitness")
    fitness_trees = [Tree(node, sch, fitness=None) for node in fitness_individuals]
    
    print("Evaluating fitness trees on historical data...\n")
    for i, tree in enumerate(fitness_trees):
        # print(f"Evaluating tree {i+1}/{len(fitness_trees)}...")
        tree.calculate_fitness(players)
        if (i+1) % 100 == 0:
            print(f"  Completed {i+1}/{len(fitness_trees)} trees")
        # print(f"Tree {i+1}: MSE = {tree.fitness:.2f}, Structure = {tree.to_string()}")

    print("\n=== Creating fitness wheel ===")
    fitness_wheel = population.make_wheel(fitness_trees)
    print(f"Best initial ranking error: {min(t.fitness for t in fitness_trees):.4f}")
    print(f"Worst initial ranking error: {max(t.fitness for t in fitness_trees):.4f}\n")
    
    # Track evolution progress
    generation_stats = []
    best_fitness_per_gen = []
    avg_fitness_per_gen = []
    worst_fitness_per_gen = []
    
    fitness_counter = 0
    while fitness_counter < episodes:
        # Recompute selection wheel each generation to reflect updated fitnesses
        fitness_wheel = population.make_wheel(fitness_trees)
        crossover = False
        parent1_index = population.selector(fitness_wheel)
        parent2_index = population.selector(fitness_wheel)
        if genetic_ops.should_crossover():
            crossover = True
            child1, child2 = genetic_ops.subtree_crossover(fitness_trees[parent1_index].copy(), fitness_trees[parent2_index].copy(), 5)
            
            # Evaluate children fitness
            child1.calculate_fitness(players)
            child2.calculate_fitness(players)
            
            worst_tree1 = max(fitness_trees, key=lambda t: t.fitness)
            if child1.fitness < worst_tree1.fitness:
                fitness_trees.remove(worst_tree1)
                fitness_trees.append(child1)
            worst_tree2 = max(fitness_trees, key=lambda t: t.fitness)
            if child2.fitness < worst_tree2.fitness:
                fitness_trees.remove(worst_tree2)
                fitness_trees.append(child2)
        
        if genetic_ops.should_mutate() and not crossover:
            parent_index = population.selector(fitness_wheel)
            mutated_tree = genetic_ops.subtree_mutation(fitness_trees[parent_index].copy(), 5)
            
            # Evaluate mutated tree fitness
            mutated_tree.calculate_fitness(players)
            
            worst_tree = max(fitness_trees, key=lambda t: t.fitness)
            if mutated_tree.fitness < worst_tree.fitness:
                fitness_trees.remove(worst_tree)
                fitness_trees.append(mutated_tree)

        
        # Track statistics for this generation
        best_fitness = min(t.fitness for t in fitness_trees)
        avg_fitness = sum(t.fitness for t in fitness_trees) / len(fitness_trees)
        worst_fitness = max(t.fitness for t in fitness_trees)
        
        best_fitness_per_gen.append(best_fitness)
        avg_fitness_per_gen.append(avg_fitness)
        worst_fitness_per_gen.append(worst_fitness)
        
        fitness_counter += 1
    
    print("\n=== Best Fitness Tree ===")
    best_tree = min(fitness_trees, key=lambda t: t.fitness)
    print(f"Ranking Error = {best_tree.fitness:.4f}")
    print(f"Structure = {best_tree.to_string()}")
    
    # Plot evolution progress
    print("\n=== Plotting Evolution Progress ===")
    generations = list(range(1, episodes + 1))
    
    plt.figure(figsize=(10, 6))
    plt.plot(generations, best_fitness_per_gen, label='Best Ranking Error', color='green', linewidth=2)
    plt.plot(generations, avg_fitness_per_gen, label='Average Ranking Error', color='blue', linewidth=2)
    plt.plot(generations, worst_fitness_per_gen, label='Worst Ranking Error', color='red', linewidth=2)
    
    plt.xlabel('Generation', fontsize=12)
    plt.ylabel('Ranking Error (Lower = Better)', fontsize=12)
    plt.title('GP Evolution: Fitness Function Learning Performance', fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    print("Graph displayed!")

    # Per-week ranking report for the best tree
    print("\n=== Per-Week Ranking Report (Best Tree) ===")

    weeks_data = best_tree.get_gp_ranking_data()
    for week_name, week_info in weeks_data.items():
        rankings = week_info.get("rankings", [])
        print(f"\n{week_name}:")
        sch = best_tree.sch
        teams_with_scores = []
        for entry in rankings:
            actual_place = entry.get("place")
            player_names = entry.get("players", [])
            week_num = int(str(week_name).split('_')[1])

            team_players = []
            for name in player_names:
                player = next((p for p in players if p.get("name") == name), None)
                if player:
                    team_players.append(player)

            features = best_tree.get_team_features(team_players, target_week=week_num)
            predicted_score = best_tree.root.evaluate(features)
            teams_with_scores.append({
                'actual_place': actual_place,
                'predicted_score': predicted_score,
                'players': player_names
            })

        teams_with_scores.sort(key=lambda x: x['predicted_score'], reverse=True)

        for idx, t in enumerate(teams_with_scores, start=1):
            print(f"  Pred {idx:>2} | Act {t['actual_place']:>2} | Score {t['predicted_score']:.4f} | {', '.join(t['players'][:3])}...")

    individuals = population.ramped_half_and_half(2000, depths, team_handler.make_random_valid_team)
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
