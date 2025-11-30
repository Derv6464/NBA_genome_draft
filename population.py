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
        
    def make_wheel(self):
        pop_scores = [(team, team.calculate_fitness()) for team in self.individuals]
        total = sum(pop_scores[i][1] for i in range(len(pop_scores)))
        wheel = [(person, fitness/total) for person, fitness in pop_scores]
	
        return wheel
	

    def selector(wheel):
        pop = [person for person, _ in wheel]
        percents = [percent for _, percent in wheel]
        wheel_range = sum(percents)
        cumulative_probs= []
	
        next_val = 0		
        for percent in percents:
            new_next_val = next_val+percent
            cumulative_probs.append([next_val, new_next_val])
            next_val = new_next_val
		
        r = random.uniform(0, wheel_range)
	
        for  WheelCream, cumulative_prob  in enumerate(cumulative_probs):
            if r > (cumulative_prob[0]) and r < (cumulative_prob[1]):
                return WheelCream
