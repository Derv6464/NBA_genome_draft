# NBA_genome_draft

This project uses a genetic algorithm to draft an optimal NBA fantasy team based on player performance data. The algorithm evolves a population of teams over multiple generations, selecting the best-performing teams and applying crossover and mutation to create new teams. The goal is to maximize the total points scored by the team while adhering to a salary cap.

## Setup

```bash
uv sync
uv run main.py
```

## Command Line Arguments
``` bash
usage: main.py [-h] [-w WEEK] [-e EPISODES] [-p POPULATION] [-s SALARY]
```

``` bash
options:
  -h, --help            show this help message and exit
  -w WEEK, --week WEEK  Week number to generate team for
  -e EPISODES, --episodes EPISODES
                        Number of generations to run
  -p POPULATION, --population POPULATION
                        Population size for each generation
  -s SALARY, --salary SALARY
                        Maximum salary cap for the team
```

## Outputs
The program generates several outputs, including:
- A printed summary of the best team drafted.
- Graphs showing the fitness progression over generations and weekly scores compared to benchmark teams.

