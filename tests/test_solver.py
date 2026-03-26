import unittest
from ortools.constraint_solver import pywrapcp
from solver import solve_cvrp, create_manager, create_routing_model, cost_evaluator
from utils import load_data

def test_solver_runs():
    data = load_data("data/cvrp_problem_data.json")
    solution = solve_cvrp(data)

    assert solution["success"] is True
    assert isinstance(solution["routes"], list)

class TestRoutingFunctions(unittest.TestCase):

    def setUp(self):
        # Example distance matrix
        self.distance_matrix = [
            [0, 10, 15],
            [10, 0, 20],
            [15, 20, 0]
        ]
        self.num_nodes = len(self.distance_matrix)
        self.num_vehicles = 1
        self.depot = 0

        # Create manager and routing model
        self.manager = create_manager(self.num_nodes, self.num_vehicles, self.depot)
        self.routing = create_routing_model(self.manager)

    def test_create_manager(self):
        self.assertEqual(self.manager.GetNumberOfNodes(), self.num_nodes)
        self.assertEqual(self.manager.GetNumberOfVehicles(), self.num_vehicles)

    def test_create_routing_model(self):
        self.assertIsInstance(self.routing, pywrapcp.RoutingModel)

    def test_cost_evaluator(self):
        transit_index = cost_evaluator(self.routing, self.manager, self.distance_matrix)
        self.assertIsInstance(transit_index, int)  # should return a callback index

if __name__ == "__main__":
    unittest.main()