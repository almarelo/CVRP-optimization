from pathlib import Path
from utils import load_data, verify_constraints 
from solver import solve_cvrp
from other_solvers import solve_cvrp_cp, solve_cvrp_greedy, solve_cvrp_greedy_parallel
import time
 

def main():
    #Load data from file
    data=load_data("data/cvrp_problem_data.json")

    start_time = time.perf_counter()
    solution1 = solve_cvrp(data)
    print("Solution obtained by OR-Tools Routing Library -- with parametres: PATH_CHEAPEST_ARC, GUIDED_LOCAL_SEARCH, 10")
    print(solution1)
    end_time = time.perf_counter()
    elapsed_time1 = end_time - start_time
    print(f"Solution obtained in {elapsed_time1:.4f} seconds\n")
    
    start_time = time.perf_counter()
    solution2 = solve_cvrp_cp(data)
    print("Solution obtained by OR-Tools CP-Solver")
    print(solution2)
    end_time = time.perf_counter()
    elapsed_time2 = end_time - start_time
    print(f"Solution obtained in {elapsed_time2:.4f} seconds\n")   

    start_time = time.perf_counter()
    solution3 = solve_cvrp_greedy(data)
    print("Solution obtained by Greedy Solver")
    print(solution3)
    end_time = time.perf_counter()
    elapsed_time3 = end_time - start_tim
    print(f"Solution obtained in {elapsed_time3:.4f} seconds\n") 

    start_time = time.perf_counter()
    solution4 = solve_cvrp_greedy_parallel(data)
    print("Solution obtained by Greedy Parallel Solver")
    print(solution4)
    end_time = time.perf_counter()
    elapsed_time4 = end_time - start_time
    print(f"Solution obtained in {elapsed_time4:.4f} seconds\n")   

if __name__ == "__main__":
    main()
