from team_handler import TeamHandler
from population import Population
from genetic_operators import GeneticOperators
from team import Team
from schedule import Schedule
from tree.tree import Tree
from comparitor import Comparitor

import matplotlib.pyplot as plt
import random
from datetime import datetime

class Runner:
    def __init__(self, episodes, population_size, player_data, games_data, teams_data, max_salary, generate_team_for_week, comp_teams):
        self.episode_count = episodes
        self.population_size = population_size
        self.players = player_data
        self.sch = Schedule(games_data)
        self.teams = teams_data
        self.max_salary = max_salary
        self.propulation = Population()
        self.elitism_count = int(population_size * 0.001)

        self.genetic_ops = GeneticOperators(self.players)
        self.team_handler = TeamHandler(self.players, self.sch, max_salary, generate_team_for_week)
        self.comparitor = Comparitor(self.team_handler, comp_teams, 3, generate_team_for_week)



    def run_genetic_programming(self, episodes, players, sch, genetic_ops):
        episodes = self.episode_count
        fitness_individuals = self.population.ramped_half_and_half(size=1000, grow_funcs=5, type="fitness")
        fitness_trees = [Tree(node, self.sch, fitness=None) for node in fitness_individuals]

        print("Evaluating fitness trees on historical data...\n")
        for i, tree in enumerate(fitness_trees):
            # print(f"Evaluating tree {i+1}/{len(fitness_trees)}...")
            tree.calculate_fitness(self.population)
            if (i+1) % 100 == 0:
                print(f"  Completed {i+1}/{len(fitness_trees)} trees")
            # print(f"Tree {i+1}: MSE = {tree.fitness:.2f}, Structure = {tree.to_string()}")

        print("\n=== Creating fitness wheel ===")
        fitness_wheel = self.population.make_wheel(fitness_trees)
        print(f"Best initial ranking error: {min(t.fitness for t in fitness_trees):.4f}")
        print(f"Worst initial ranking error: {max(t.fitness for t in fitness_trees):.4f}\n")

        # Track evolution progress
        best_fitness_per_gen = []
        avg_fitness_per_gen = []
        worst_fitness_per_gen = []

        fitness_counter = 0
        while fitness_counter < episodes:
            # Recompute selection wheel each generation to reflect updated fitnesses
            fitness_wheel = self.population.make_wheel(fitness_trees)
            crossover = False
            parent1_index = self.population.selector(fitness_wheel)
            parent2_index = self.population.selector(fitness_wheel)
            if genetic_ops.should_crossover():
                crossover = True
                child1, child2 = genetic_ops.subtree_crossover(fitness_trees[parent1_index].copy(), fitness_trees[parent2_index].copy(), 5)

                # Evaluate children fitness
                child1.calculate_fitness(self.players)
                child2.calculate_fitness(self.players)

                worst_tree1 = max(fitness_trees, key=lambda t: t.fitness)
                if child1.fitness < worst_tree1.fitness:
                    fitness_trees.remove(worst_tree1)
                    fitness_trees.append(child1)
                worst_tree2 = max(fitness_trees, key=lambda t: t.fitness)
                if child2.fitness < worst_tree2.fitness:
                    fitness_trees.remove(worst_tree2)
                    fitness_trees.append(child2)

            if genetic_ops.should_mutate() and not crossover:
                parent_index = self.population.selector(fitness_wheel)
                mutated_tree = genetic_ops.subtree_mutation(fitness_trees[parent_index].copy(), 5)

                # Evaluate mutated tree fitness
                mutated_tree.calculate_fitness(self.players)

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


    def run_programing_results(self):

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
            teams_with_scores = []
            for entry in rankings:
                actual_place = entry.get("place")
                player_names = entry.get("players", [])
                week_num = int(str(week_name).split('_')[1])

                team_players = []
                for name in player_names:
                    player = next((p for p in self.players if p.get("name") == name), None)
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

  
        plt.plot([stat["generation"] for stat in generation_stats], [stat["best_fitness"] for stat in generation_stats], label="Best Fitness")
        plt.plot([stat["generation"] for stat in generation_stats], [stat["average_fitness"] for stat in generation_stats], label="Average Fitness")
        plt.plot([stat["generation"] for stat in generation_stats], [stat["worst_fitness"] for stat in generation_stats], label="Worst Fitness")
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.title("Fitness over Generations")
        plt.legend()
        file_path = os.path.join("data/images/", f"{datetime.now()}-1.png")
        plt.savefig(file_path, bbox_inches='tight')

    def run_genetic_algorithm(self):
        episodes = self.episode_count
        individuals = [self.team_handler.make_random_valid_team() for _ in range(self.population_size)]
        
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

            next_generation = [team.copy() for team in individuals[:self.elitism_count]]
            wheel = self.population.make_wheel(individuals)

            while len(next_generation) < len(individuals):
                parent1 = self.population.selector(wheel)
                parent2 = self.population.selector(wheel)

                random.shuffle(parent1.players)
                random.shuffle(parent2.players)

                child1, child2 = self.genetic_ops.crossover(parent1.copy(), parent2.copy())
                child1.re_evaluate()
                child2.re_evaluate()
                next_generation.append(child1)
                next_generation.append(child2)

            for i in range(self.elitism_count, len(next_generation)):
                if random.random() < 0.2:
                    self.genetic_ops.mutate(next_generation[i].players)
                    next_generation[i].re_evaluate()

            individuals = next_generation
            counter += 1
            print(f"Generation {counter} completed in {datetime.now() - ep_timer}")

        print(f"\nTotal Time Taken: {datetime.now() - total_timer}")
        best_team = max(individuals, key=lambda team: team.fitness)

        print("\n=== Final Best Team ===")
        self._print_team(best_team)

        best_team.save_team()

        return best_team

    def run_algorithim_results(self, best_team):
        self.comparitor.compare_fitness(best_team)
        self.comparitor.compare_weekly_scores(best_team)
        self.comparitor.compare_days_scores(best_team, [self.generate_team_for_week], [1,2,3,4,5,6,7])
    
        self.comparitor.graph_fitness()
        self.comparitor.graph_weekly_scores()
        self.comparitor.graph_days_scores(best_team, [self.generate_team_for_week], [1,2,3,4,5,6,7])

    def _print_team(team: Team):
        print(f"fitness: {team.calculate_fitness()}")
        print(f"Cost: {team.get_team_salary()}")
        print(f"is valid {team.check_team_validity()} (Salary Cap: {team.check_player_salary()}, Position Cap: {team.check_player_position()}, Team Cap: {team.check_player_per_team()})")
        for player in team.players:
            print(f"{player.get('name')} - {player.get('team')} - {player.get('position')} - Salary: {player.get('salary')} - Total Points: {player.get('total_points')}")
