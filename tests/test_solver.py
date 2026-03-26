import unittest
from ortools.constraint_solver import pywrapcp
from solver import solve_cvrp, create_manager, create_routing_model, distance_callback, cost_evaluator
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
        #self.assertEqual(self.manager.Start(0), self.depot)
        # Check start and end indices for all vehicles
        # starting_at_depot = all(self.manager.Start(v) == self.depot for v in range(self.num_vehicles))
        # ending_at_depot   = all(self.manager.End(v) == self.depot for v in range(self.num_vehicles))
        # self.assertTrue(starting_at_depot)
        # self.assertTrue(ending_at_depot)

    def test_create_routing_model(self):
        self.assertIsInstance(self.routing, pywrapcp.RoutingModel)

    def test_distance_callback(self):
        # test some known distances
        self.assertEqual(distance_callback(0, 1, self.manager, self.distance_matrix), 10)
        self.assertEqual(distance_callback(1, 2, self.manager, self.distance_matrix), 20)
        self.assertEqual(distance_callback(2, 0, self.manager, self.distance_matrix), 15)

    def test_cost_evaluator(self):
        def callback(from_index, to_index):
            return distance_callback(from_index, to_index, self.manager, self.distance_matrix)

        transit_index = cost_evaluator(self.routing, callback)
        self.assertIsInstance(transit_index, int)  # should return a callback index

if __name__ == "__main__":
    unittest.main()