from solver import solve_cvrp
from utils import load_data

def test_solver_runs():
    data = load_data("data/cvrp_problem_data.json")
    solution = solve_cvrp(data)

    assert solution["success"] is True
    assert isinstance(solution["routes"], list)