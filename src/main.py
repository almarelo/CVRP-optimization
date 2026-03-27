from pathlib import Path
from utils import load_data, verify_constraints 
from solver import solve_cvrp
from other_solvers import solve_cvrp_cp, solve_cvrp_greedy, solve_cvrp_greedy_parallel
import time
 

def main():
    #Load data from file
    data=load_data("data/cvrp_problem_data.json")
    #print(data)

    start_time = time.perf_counter()
    solution1 = solve_cvrp(data)
    print(solution1)
    end_time = time.perf_counter()
    elapsed_time1 = end_time - start_time
    print(f"Solution obtained with OR-Tools routing library in {elapsed_time1:.4f} seconds")
    


    start_time = time.perf_counter()
    solution2 = solve_cvrp_sat(data)
    print(solution2)
    end_time = time.perf_counter()
    elapsed_time2 = end_time - start_time
    print(f"Solution obtained with OR-Tools CP-SAT solver in {elapsed_time2:.4f} seconds")   


    start_time = time.perf_counter()
    solution3 = solve_cvrp_greedy(data)
    print(solution3)
    end_time = time.perf_counter()
    elapsed_time3 = end_time - start_time
    print(f"Solution obtained with greedy solver in {elapsed_time3:.4f} seconds") 

    start_time = time.perf_counter()
    solution4 = solve_cvrp_greedy_parallel(data)
    print(solution4)
    end_time = time.perf_counter()
    elapsed_time4 = end_time - start_time
    print(f"Solution obtained with greedy parallel solver in {elapsed_time4:.4f} seconds")   
    
    # Verify solution
    #verify_constraints(solution1, data)
    #verify_constraints(solution2, data)

    

if __name__ == "__main__":
    main()