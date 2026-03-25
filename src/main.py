from pathlib import Path
from utils import load_data

def main():
    #Load data from file
    data=load_data("data/cvrp_problem_data.json")
    print(data)

if __name__ == "__main__":
    main()