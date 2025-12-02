import random

class GeneticOperators:
    def __init__(self, players):
        self.players = players

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

        print(f"Crossover between teams at point {crossover_point}")
