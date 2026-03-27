from pathlib import Path
from utils import load_data, verify_constraints 
from solver import solve_cvrp
import time
 

def main():
    #Load data from file
    data=load_data("data/cvrp_problem_data.json")

    start_time = time.perf_counter()
    solution1 = solve_cvrp(data)
    print(solution1)
    end_time = time.perf_counter()
    elapsed_time1 = end_time - start_time
    print(f"Solution obtained with OR-Tools routing library in {elapsed_time1:.4f} seconds")
    
if __name__ == "__main__":
    main()