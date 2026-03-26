import pytest
from utils import load_data, verify_constraints

def test_load_data():
    data = load_data("data/cvrp_problem_data.json")
    assert isinstance(data, dict)
    assert "nodes" in data
    assert "vehicles" in data
    assert "demands" in data
    assert "distance_matrix" in data
    assert "constraints" in data

def test_verify_constraints_success():
    data = {
        "constraints": {
            "each_node_visited_once": True,
            "vehicles_start_and_end_at_depot": True,
            "vehicle_capacity_respected": True
        },
        "nodes": {"delivery_locations": [1, 2, 3]},
        "demands": [0, 10, 20, 30],
        "vehicles": {"capacity_per_vehicle": 100}
    }
    solution = {
        "routes": [[0, 1, 2, 0], [0, 3, 0]]
    }
    # Should not raise exception
    verify_constraints(solution, data)

def test_verify_constraints_missing_node():
    data = {
        "constraints": {
            "each_node_visited_once": True,
            "vehicles_start_and_end_at_depot": False,
            "vehicle_capacity_respected": False
        },
        "nodes": {"delivery_locations": [1, 2, 3, 4]}
    }
    solution = {
        "routes": [[0, 1, 2, 0], [0, 3, 0]] # Node 4 is not visited
    }
    with pytest.raises(ValueError, match="Not all nodes were visited"):
        verify_constraints(solution, data)

def test_verify_constraints_invalid_depot():
    data = {
        "constraints": {
            "each_node_visited_once": False,
            "vehicles_start_and_end_at_depot": True,
            "vehicle_capacity_respected": False
        }
    }
    solution = {
        "routes": [[1, 2, 0], [0, 3, 0]]  # route 1 does not start at 0
    }
    with pytest.raises(ValueError, match="Not all vehicles start and end at depot"):
        verify_constraints(solution, data)

def test_verify_constraints_capacity_exceeded():
    data = {
        "constraints": {
            "each_node_visited_once": False,
            "vehicles_start_and_end_at_depot": False,
            "vehicle_capacity_respected": True
        },
        "demands": [0, 50, 60, 20],
        "vehicles": {"capacity_per_vehicle": 100}
    }
    solution = {
        "routes": [[0, 1, 2, 0], [0, 3, 0]]  # route 1 demand = 50 + 60 = 110 > 100
    }
    with pytest.raises(ValueError, match="Not all vehicles capacity respected"):
        verify_constraints(solution, data)