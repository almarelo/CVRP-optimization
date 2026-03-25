import json
from pathlib import Path


def load_data(path: str):
    """
    Load a CVRP instance from a JSON file.

    Returns a dictionary with:
    -num_nodes
    -num_vehicles
    -capacity
    -demands
    -distance_matrix
    -constraints
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r") as f:
        data = json.load(f)

    #Validation
    required_keys = [
        "nodes",
        "vehicles",
        "demands",
        "distance_matrix",
        "constraints"
    ]


    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")

    
    num_nodes = data["nodes"]


    if len(data["distance_matrix"]) != len(data["demands"]):
        raise ValueError("Distance matrix and demands size mismatch")

    if 

    return data