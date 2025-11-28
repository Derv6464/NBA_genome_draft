from data_generator import DataGenerator
from team_handler import TeamHandler
from population import Population
from fitness import Fitness
from genetic_operators import GeneticOperators


def main():
    max_salary = 100

    #loading in player & game data
    data_generator = DataGenerator("data")
    players, games = data_generator.get_existing_data()

    team_handler = TeamHandler(players, games, max_salary)
    fitness = Fitness(team_handler)
    genetic_ops = GeneticOperators(players)
    population = Population()

    team = team_handler.get_best_players()
    depths = [team_handler.get_best_players, team_handler.get_random_no_caps, team_handler.get_random_position_cap, team_handler.get_random_team_cap, team_handler.get_random_salary_cap]
    
    individuals = population.ramped_half_and_half(10, depths, team_handler.make_random_valid_team)

    for i, team in enumerate(individuals):
        print(f"Team: {i}")
        print(f"fitness: {fitness.evaluate_team(team)}")
        print(f"Cost: {team_handler.get_team_salary(team)}")
        print(f"is valid {team_handler.check_team_validity(team)}")

    #genetic_ops.mutate(team)
    #genetic_ops.crossover(team, team2)
   #fitness.evaluate_team(team)
    #fitness.evaluate_team(team2)

if __name__ == "__main__":
    main()
