from pathlib import Path
from utils import load_data
from solver import solve_cvrp

 

def main():
    #Load data from file
    data=load_data("data/cvrp_problem_data.json")
    #print(data)

    #Solve CVRP
    solution = solve_cvrp(data)

    print(solution)

if __name__ == "__main__":
    main()