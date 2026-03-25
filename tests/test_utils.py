from utils import load_data


def test_load_data():
    data = load_data("data/cvrp_problem_data.json")

    assert isinstance(data, dict)

    assert "nodes" in data
    assert "vehicles" in data
    assert "demands" in data
    assert "distance_matrix" in data
    assert "constraints" in data
    