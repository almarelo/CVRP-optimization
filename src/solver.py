from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from typing import Dict, Any


CVRPInput = Dict[str, Any]
CVRPModel = Dict[str, Any]
CVRPOutput = Dict[str, Any]

def create_cvrp_model(data: CVRPInput) -> CVRPModel:
    """
    Instantiate the routing problem from the data.
    """
    num_nodes = data["nodes"]["total"]
    depot = data["nodes"]["depot"]
    num_vehicles = data["vehicles"]["count"]
    vehicle_capacities = [data["vehicles"]["capacity_per_vehicle"]] * num_vehicles
    demands = data["demands"]   
    distance_matrix = data["distance_matrix"]

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot)

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    
    return {
        "num_nodes": num_nodes,
        "depot": depot,
        "num_vehicles": num_vehicles,
        "vehicle_capacities": vehicle_capacities,
        "demands": demands,
        "distance_matrix": distance_matrix,
        "manager": manager,
        "routing": routing
    }


def cost_evaluator(routing, manager, distance_matrix):
    """
    Sets the arc costs for all vehicles and returns a distance callback index.
    """
    # Nested callback function to access the distances.
    def distance_callback(from_index, to_index):
        """
        Returns the distance between two nodes.
        Has access to manager and distance_matrix via closure.
        """
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]
    # Register the callback 
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # Set the arc costs equal to the distances for all vehicles.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    return transit_callback_index


def demand_evaluator(routing, manager, demands, vehicle_capacities):
    """
    Sets the capacity dimension for all vehicles and returns a demand callback index.
    """
    # Nested callback function to acces the demands.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    # Register the callback.
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    # Add a dimension to the routing model to track the capacity of each vehicle.
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        vehicle_capacities,  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity",
    )
    return demand_callback_index

def search_parameters(first_solution_strategy   : str, local_search_metaheuristic: str, time_limit: int) -> pywrapcp.DefaultRoutingSearchParameters:
    """
    Sets the search parameters for the routing model, the search strategies are fixed for now, to be modified later.
    """ 
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    # Setting first solution heuristic.
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    # Setting local search metaheuristic.
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    # Setting time limit.
    search_parameters.time_limit.FromSeconds(time_limit)

    return search_parameters


def solve_cvrp(data: CVRPInput) -> CVRPOutput:
    """
    Solves CVRP with OR-Tools routing library.
    """ 
    model = create_cvrp_model(data)
    manager = model["manager"]
    routing = model["routing"]
    distance_matrix = model["distance_matrix"]
    demands = model["demands"]
    vehicle_capacities = model["vehicle_capacities"]
    num_vehicles = model["num_vehicles"]

    # Register a transit callback for the cumulated distance of a truck in a route.
    transit_callback_index = cost_evaluator(routing, manager, distance_matrix)

    # Register a transit callback for the capacity of a truck updated based on the demands of a route.
    demand_callback_index = demand_evaluator(routing, manager, demands, vehicle_capacities)
    


    # Get parameters
    params = search_parameters('PATH_CHEAPEST_ARC', 'GUIDED_LOCAL_SEARCH', 1)

    # Solve the problem.
    solution = routing.SolveWithParameters(params)

    # Return solution.
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
