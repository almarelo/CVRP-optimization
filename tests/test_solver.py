import unittest
from ortools.constraint_solver import pywrapcp
from solver import solve_cvrp, create_cvrp_model, cost_evaluator, demand_evaluator
from utils import load_data

def test_solver_runs():
    data = load_data("data/cvrp_problem_data.json")
    solution = solve_cvrp(data)

    assert solution["success"] is True
    assert isinstance(solution["routes"], list)

class TestRoutingFunctions(unittest.TestCase):

    def setUp(self):
        # Example data
        self.data = {
            "nodes": {"total": 3, "depot": 0},
            "vehicles": {"count": 1, "capacity_per_vehicle": 100},
            "demands": [0, 10, 20],
            "distance_matrix": [
                [0, 10, 15],
                [10, 0, 20],
                [15, 20, 0]
            ]
        }
        self.model = create_cvrp_model(self.data)
        self.manager = self.model["manager"]
        self.routing = self.model["routing"]

    def test_create_cvrp_model(self):
        self.assertEqual(self.manager.GetNumberOfNodes(), 3)
        self.assertEqual(self.manager.GetNumberOfVehicles(), 1)
        self.assertIsInstance(self.routing, pywrapcp.RoutingModel)

    def test_cost_evaluator(self):
        transit_index = cost_evaluator(self.routing, self.manager, self.data["distance_matrix"])
        self.assertIsInstance(transit_index, int)

if __name__ == "__main__":
    unittest.main()