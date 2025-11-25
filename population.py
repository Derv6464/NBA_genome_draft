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




        

    