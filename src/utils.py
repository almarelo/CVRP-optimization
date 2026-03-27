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

    
    return data


    

def verify_constraints(solution, data):
    if data["constraints"]["each_node_visited_once"]:
        visited_nodes = []
        for route in solution["routes"]:
            for node in route:
                if node != 0:
                    visited_nodes.append(node)
        if sorted(visited_nodes) != sorted(data["nodes"]["delivery_locations"]):
            raise ValueError("Not all nodes were visited")
    
    if data["constraints"]["vehicles_start_and_end_at_depot"]:
        for route in solution["routes"]:
            if route[0] != 0 or route[-1] != 0:
                raise ValueError("Not all vehicles start and end at depot")
    
    if data["constraints"]["vehicle_capacity_respected"]:
        for route in solution["routes"]:
            if sum(data["demands"][node] for node in route) > data["vehicles"]["capacity_per_vehicle"]:
                raise ValueError("Not all vehicles capacity respected")
    
    return True



    