import random
from tree.tree import Tree
from tree.treeNode import TreeNode

OPERATORS = ["+", "-", "*" , "/", "min", "max"]
# VARIABLES = [
#     "weighted_score", "avg_weekly_score", "total_weeks",
#     "salary", "salary_penalty",
#     "games_penalty", "position_penalty",
#     "team_count_penalty", "duplication_penalty",
#     "fc_count", "bc_count"
# ]

VARIABLES = [
    "salary",
    "points", 
    "rebounds",
    "assists",
    "blocks",
    "steals",
    "fc_count",
    "bc_count",
    "weighted_score",
    "avg_weekly_score",
    "total_weeks",
    "games_count",
    "points_per_salary",
]

class Population:
    def __init__(self):
        self.individuals = []

    def ramped_half_and_half(self, size, grow_funcs=None, full_func=None, type = None):
        individuals = []      

        if type == "fitness":
            depths = list(range(2, grow_funcs + 1))
            per_depth = size // len(depths)
            remainder = size % len(depths)
            for depth in depths:
                num_trees = per_depth + (1 if remainder > 0 else 0)
                remainder -= 1
                
                half = num_trees // 2
                
                for _ in range(half):
                    individuals.append(self.generate_full_tree(depth))
                
                for _ in range(num_trees - half):
                    individuals.append(self.generate_grow_tree(depth))

        else:
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
    
    def generate_full_tree(self, max_depth, current_depth=0):
        if current_depth == max_depth:
            value = random.choice(VARIABLES)
            return TreeNode(value)
        
        operator = random.choice(OPERATORS)
        node = TreeNode(operator)
        
        # Generate left and right subtrees
        node.left = self.generate_full_tree(max_depth, current_depth + 1)
        node.right = self.generate_full_tree(max_depth, current_depth + 1)
        
        # If both children are leaves with same variable, regenerate right child
        if (node.left.is_leaf() and node.right.is_leaf() and 
            node.left.value == node.right.value and 
            isinstance(node.left.value, str)):
            # Choose a different variable for right child
            different_vars = [v for v in VARIABLES if v != node.left.value]
            if different_vars:
                node.right.value = random.choice(different_vars)
        
        return node

    def generate_grow_tree(self, max_depth, current_depth=0):
        if current_depth == max_depth:
            value = random.choice(VARIABLES)
            return TreeNode(value)
        
        if random.random() < 0.3: 
            value = random.choice(VARIABLES)
            return TreeNode(value)
        
        operator = random.choice(OPERATORS)
        node = TreeNode(operator)
        
        # Generate left and right subtrees
        node.left = self.generate_grow_tree(max_depth, current_depth + 1)
        node.right = self.generate_grow_tree(max_depth, current_depth + 1)
        
        # If both children are leaves with same variable, regenerate right child
        if (node.left.is_leaf() and node.right.is_leaf() and 
            node.left.value == node.right.value and 
            isinstance(node.left.value, str)):
            # Choose a different variable for right child
            different_vars = [v for v in VARIABLES if v != node.left.value]
            if different_vars:
                node.right.value = random.choice(different_vars)
        
        return node
        
    def make_wheel(self, individuals):
        # Invert errors so lower fitness (error) gets higher selection probability
        eps = 1e-9
        raw = []
        for team in individuals:
            inv = 1.0 / (eps + float(team.fitness)) if team.fitness is not None else 0.0
            raw.append((team, inv))

        total = sum(weight for _, weight in raw)
        if total <= 0:
            # Fallback to uniform selection if something went wrong
            prob = 1.0 / max(1, len(raw))
            return [(person, prob) for person, _ in raw]

        wheel = [(person, weight / total) for person, weight in raw]
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

