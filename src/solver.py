from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from typing import Dict, Any


CVRPInput = Dict[str, Any]
CVRPModel = Dict[str, Any]
CVRPOutput = Dict[str, Any]


# Define default variables
num_vehicles = 2
num_nodes = 21
depot = 0

# Create manager
def create_manager(num_nodes, num_vehicles, depot):
    return pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot)
    
# Create routing model
def create_routing_model(manager):
    return pywrapcp.RoutingModel(manager)
    
    
# Convert from routing variable Index to distance matrix NodeIndex.
def distance_callback(from_index, to_index, manager, distance_matrix):
    """
    Returns the distance between the two nodes.
    """
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]

#Assign the cost of every arc equal to the distance for all vehicles
  
def cost_evaluator(routing, distance_callback):
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    return transit_callback_index



def solve_cvrp(data: CVRPInput) -> CVRPOutput:
    """
    Solver with OR-tools
    """
    
    # Simple dummy solution: assign each node to first vehicle in order
    routes = [[0] + list(range(1, num_nodes)) + [0]]  # single route covering all
    while len(routes) < num_vehicles:
        routes.append([0, 0])  # empty routes for extra vehicles
    vehicle_distances = [1000]
    while len(routes) < num_vehicles:
        vehicle_distances.append([0, 0])  # distance 0 for extra vehicles

    total_distance = sum(vehicle_distances) 
    vehicle_loads = [sum(data["demands"])] + [0]*(num_vehicles-1)

    return {
        "routes": routes,
        "vehicle_distances": vehicle_distances,
        "total_distance": total_distance,
        "vehicle_loads": vehicle_loads,
        "success": True
    }

def fake_solve_cvrp(data: CVRPInput) -> CVRPOutput:
    """
    Black-box placeholder for CVRP solver.
    Currently just returns a dummy solution.
    Replace this with OR-Tools logic later.
    """
    num_vehicles = data["vehicles"]["count"]
    num_nodes = data["nodes"]["total"]
    
    # Simple dummy solution: assign each node to first vehicle in order
    routes = [[0] + list(range(1, num_nodes)) + [0]]  # single route covering all
    while len(routes) < num_vehicles:
        routes.append([0, 0])  # empty routes for extra vehicles
    vehicle_distances = [1000]
    while len(routes) < num_vehicles:
        vehicle_distances.append([0, 0])  # distance 0 for extra vehicles

    total_distance = sum(vehicle_distances) 
    vehicle_loads = [sum(data["demands"])] + [0]*(num_vehicles-1)

    return {
        "routes": routes,
        "vehicle_distances": vehicle_distances,
        "total_distance": total_distance,
        "vehicle_loads": vehicle_loads,
        "success": True
    }