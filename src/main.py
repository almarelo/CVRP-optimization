from pathlib import Path
from utils import load_data, verify_constraints 
from solver import solve_cvrp
import time
import json
 

def main():
    #Load data from file
    data=load_data("data/cvrp_problem_data.json")
    
    # Solve and print solution
    solution1 = solve_cvrp(data)
    print(solution1)
    
    # Custom format to keep numerical vectors (lists) on a single row
    json_lines = []
    for k, v in solution1.items():
        json_lines.append(f'    "{k}": {json.dumps(v)}')
    json_str = "{\n" + ",\n".join(json_lines) + "\n}\n"

    # Save solution to results/solution.json, overwriting any previous content
    with open("results/solution.json", "w") as f:
        f.write(json_str)
    print("Solution saved to results/solution.json")

if __name__ == "__main__":
    main()