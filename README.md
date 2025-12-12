# NBA_genome_draft

This is a project that uses genetic algorithms and genetic programming to draft an optimal NBA fantasy team on a given week.

## Setup

Clone the repo:
```bash
git clone https://github.com/Derv6464/NBA_genome_draft.git
cd NBA_genome_draft
```

Install the dependencies using:

```bash
uv sync
```

Next, set up the data from fantasy site and the ESPN API. Don't touch your computer while the setup is running, as it will cause issues with data fetching.
Chrome needs to be installed for this. Run:  

```bash
uv run main.py --setup
```

## Command Line Arguments

``` bash
usage: main.py [-h] [-w WEEK] [-e EPISODES] [-p POPULATION] [-s SALARY] [--setup] [--ga] [--gp]

options:
  -h, --help            show this help message and exit
  -w WEEK, --week WEEK  Week number to generate team for
  -e EPISODES, --episodes EPISODES
                        Number of generations to run
  -p POPULATION, --population POPULATION
                        Population size for each generation
  -s SALARY, --salary SALARY
                        Maximum salary cap for the team
  --setup               Whether to setup data from API
  --ga                  Run Genetic Algorithm
  --gp                  Run Genetic Programming
```

## Outputs

The program generates several outputs, including:

- A printed summary of the generated team drafted for GA
- A printed summary of the generated fitness function for GP
- Graphs showing the evolution of fitness scores over generations, saved in the `data/images/` directory.
- A JSON file with the best team's player IDs (from ESPN) saved in the `data/team_output.json` directory.
