import random
import population
from tree.tree import Tree
from tree.treeNode import TreeNode
from typing import Optional, Tuple, List

class GeneticOperators:
    def __init__(self, players):
        self.players = players
    
    def copy_tree(self, node: Optional[TreeNode]) -> Optional[TreeNode]:
        if node is None:
            return None
        new = TreeNode(node.value)
        new.left = self.copy_tree(node.left)
        new.right = self.copy_tree(node.right)
        return new

    def nodes_with_parents(self, root: TreeNode) -> List[Tuple[TreeNode, Optional[TreeNode], Optional[str]]]:
        out: List[Tuple[TreeNode, Optional[TreeNode], Optional[str]]] = []
        def walk(node: TreeNode, parent: Optional[TreeNode], which: Optional[str]):
            out.append((node, parent, which))
            if node.left is not None:
                walk(node.left, node, "left")
            if node.right is not None:
                walk(node.right, node, "right")
        walk(root, None, None)
        return out

    def subtree_mutation(self, parent: Tree, max_depth) -> Tree:
        if parent.root is None:
            raise ValueError("Parent tree must have a non-None root")
        
        mutated_root = self.copy_tree(parent.root)
        nodes = self.nodes_with_parents(mutated_root)
        mutation_node, mutation_parent, which_child = random.choice(nodes)
        population_instance = population.Population()
        new_subtree = population_instance.ramped_half_and_half(size =1, grow_funcs=max_depth, type = "fitness")[0]

        if mutation_parent is None:
            mutated_root = new_subtree
        else:
            if which_child == "left":
                mutation_parent.left = new_subtree
            elif which_child == "right":
                mutation_parent.right = new_subtree
            else:
                raise ValueError(f"Invalid which_child value: {which_child}")
        
        return Tree(mutated_root, parent.sch, fitness=None)

    def replace_subtree(self, root: TreeNode, parent: Optional[TreeNode], which: Optional[str], new_sub: Optional[TreeNode]) -> Optional[TreeNode]:
        if parent is None:
            return new_sub
        if which == "left":
            parent.left = new_sub
        elif which == "right":
            parent.right = new_sub
        else:
            raise ValueError("which must be 'left', 'right' or None")
        return root


    def tree_depth(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return 0
        if node.is_leaf():
            return 1
        return 1 + max(self.tree_depth(node.left), self.tree_depth(node.right))

    def subtree_crossover(self, parent1: Tree, parent2: Tree, max_depth, max_attempts: int = 10) -> Tuple[Tree, Tree]:
        if parent1.root is None or parent2.root is None:
            raise ValueError("Parents must have non-None roots")

        for _ in range(max_attempts):
            p1 = self.copy_tree(parent1.root)
            p2 = self.copy_tree(parent2.root)

            nodes1 = self.nodes_with_parents(p1)
            nodes2 = self.nodes_with_parents(p2)

            node1, parent_of_node1, which1 = random.choice(nodes1)
            node2, parent_of_node2, which2 = random.choice(nodes2)

            subtree1 = self.copy_tree(node1)
            subtree2 = self.copy_tree(node2)

            offspring1_root = self.replace_subtree(p1, parent_of_node1, which1, subtree2)
            offspring2_root = self.replace_subtree(p2, parent_of_node2, which2, subtree1)
            if self.tree_depth(offspring1_root) > max_depth or self.tree_depth(offspring2_root) > max_depth:
                continue   

            return Tree(offspring1_root, parent1.sch, fitness=None), Tree(offspring2_root, parent2.sch, fitness=None)

        return Tree(self.copy_tree(parent1.root), parent1.sch, fitness=None), Tree(self.copy_tree(parent2.root), parent2.sch, fitness=None)

    def mutate(self, team):
        team_size = len(team)
        random_player_index = random.randint(0, team_size - 1)
        new_player = random.choice(self.players)
        team[random_player_index] = new_player

        #print(f"Mutated team by replacing player at index {random_player_index} with {new_player.get('name')}")
    
    def crossover(self, team1, team2):
        team_size = len(team1.players)
        crossover_point = random.randint(1, team_size - 1)

        temp1 = team1.players[crossover_point:].copy()
        temp2 = team2.players[crossover_point:].copy()
        
        team1.players[crossover_point:] = temp2
        team2.players[crossover_point:] = temp1

        return team1, team2
    
    def should_mutate(self):
        return random.random() < 0.2

    def should_crossover(self):
        return random.random() < 0.8
