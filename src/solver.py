from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from typing import Dict, Any


CVRPInput = Dict[str, Any]
CVRPModel = Dict[str, Any]
CVRPOutput = Dict[str, Any]


# Create manager
def create_manager(num_nodes, num_vehicles, depot):
    return pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot)
    
# Create routing model
def create_routing_model(manager):
    return pywrapcp.RoutingModel(manager)
    
    

#Assign the cost of every arc equal to the distance for all vehicles
  
def cost_evaluator(routing, manager, distance_matrix):
    """
    Registers a nested distance callback and sets it as the arc cost for all vehicles.
    """
    # Nested callback function
    def distance_callback(from_index, to_index):
        """
        Returns the distance between two nodes.
        Has access to manager and distance_matrix via closure.
        """
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]
    # Register the callback and set it as the arc cost
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    return transit_callback_index



def solve_cvrp(data: CVRPInput) -> CVRPOutput:
    """
    Solver with OR-tools
    """
    # Instantiate the data problem.
    num_vehicles = data["vehicles"]["count"]
    num_nodes = data["nodes"]["total"]
    depot = data["nodes"]["depot"]
    demands = data["demands"]
    vehicle_capacities = [data["vehicles"]["capacity_per_vehicle"]] * num_vehicles
    distance_matrix = data["distance_matrix"]

    # Create the routing index manager.
    manager = create_manager(num_nodes, num_vehicles, depot)

    # Create Routing Model.
    routing = create_routing_model(manager)

    # Create and register a transit callback.
    transit_callback_index = cost_evaluator(routing, manager, distance_matrix)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        vehicle_capacities,  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity",
    )

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        routes = []
        vehicle_distances = []
        vehicle_loads = []
        total_distance = 0
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            plan_output = ""
            route_distance = 0
            route_load = 0
            route = []
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                route_load += demands[node_index]
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            
            # Add final depot node
            route.append(manager.IndexToNode(index))
            routes.append(route)
            vehicle_distances.append(route_distance)
            vehicle_loads.append(route_load)
            total_distance += route_distance

        return {
            "routes": routes,
            "vehicle_distances": vehicle_distances,
            "total_distance": total_distance,
            "vehicle_loads": vehicle_loads,
            "success": True
        }
    else:
        return {
            "success": False
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