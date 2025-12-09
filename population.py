import random

class Population:
    def __init__(self):
        self.individuals = []

    def ramped_half_and_half(self, size, grow_funcs, full_func):
        individuals = []

        depths = len(grow_funcs)
        per_depth = size // depths    
        half = per_depth // 2        

        for depth in range(depths):
            grow_func = grow_funcs[depth]

            for _ in range(half):
                individuals.append(grow_func())

            for _ in range(half):
                individuals.append(full_func())

        while len(individuals) < size:
            individuals.append(full_func())

        self.individuals = individuals
        return individuals
        
    def make_wheel(self, individuals):
        pop_scores = [(team, team.fitness) for team in individuals]
        total = sum(pop_scores[i][1] for i in range(len(pop_scores)))
        wheel = [(person, fitness/total) for person, fitness in pop_scores]
	
        return wheel

    def selector(self, wheel):
        pop = [team for team, _ in wheel]
        percents = [p for _, p in wheel]

        cumulative_probs = []
        cumulative = 0

        for p in percents:
            next_cumulative = cumulative + p
            cumulative_probs.append((cumulative, next_cumulative))
            cumulative = next_cumulative

        r = random.random()

        for i, (low, high) in enumerate(cumulative_probs):
            if low <= r < high:
                return pop[i]
