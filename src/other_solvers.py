from ortools.sat.python import cp_model
from typing import Dict, Any

def fake_solve_cvrp(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Black-box placeholder for CVRP solver.
    Returns a dummy solution.
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


def solve_cvrp_cp(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Solves CVRP with OR-Tools CP-solver.
    """
    num_nodes = data["nodes"]["total"]
    depot = data["nodes"]["depot"]
    num_vehicles = data["vehicles"]["count"]
    vehicle_capacities = [data["vehicles"]["capacity_per_vehicle"]] * num_vehicles
    demands = data["demands"]   
    distance_matrix = data["distance_matrix"]

    model = cp_model.CpModel()
    
 #Define the decision variables
    
    # x[i, j, v] is True if vehicle v travels from i to j
    x = {}
    for i in range(num_nodes):
        for j in range(num_nodes):
            for v in range(num_vehicles):
                x[i, j, v] = model.NewBoolVar(f'x_{i}_{j}_{v}')
                
    # u[i, v] is the accumulated load of vehicle v at node i
    # (after visiting node i)
    u = {}
    for i in range(num_nodes):
        for v in range(num_vehicles):
            if i == depot:
                u[i, v] = model.NewIntVar(0, 0, f'u_{i}_{v}')
            else:
                u[i, v] = model.NewIntVar(demands[i], vehicle_capacities[v], f'u_{i}_{v}')
                
    # 1. Flow conservation at each node for each vehicle
    for i in range(num_nodes):
        for v in range(num_vehicles):
            model.Add(
                sum(x[i, j, v] for j in range(num_nodes)) == 
                sum(x[j, i, v] for j in range(num_nodes))
            )
            
    # 2. Each delivery node is visited exactly once by exactly one vehicle
    for i in range(num_nodes):
        if i != depot:
            # The sum over j and v of entering arcs into node i is exactly 1
            model.AddExactlyOne(
                x[j, i, v] 
                for j in range(num_nodes) 
                for v in range(num_vehicles) 
                if j != i
            )
            
            # Prevent node self-loops for delivery nodes
            for v in range(num_vehicles):
                model.Add(x[i, i, v] == 0)

    # 3. Every vehicle starts and ends at the depot
    for v in range(num_vehicles):
        model.Add(sum(x[depot, j, v] for j in range(num_nodes)) == 1)
        # Flow conservation at depot ensures that if it leaves depot, it also returns.
        
    # 4. Miller-Tucker-Zemlin constraints for subtour elimination AND capacity
    # If vehicle v travels from i to j, u[j, v] >= u[i, v] + demands[j]
    for i in range(num_nodes):
        for j in range(num_nodes):
            if j != depot and i != j:
                for v in range(num_vehicles):
                    # Using indicator constraints
                    model.Add(u[j, v] >= u[i, v] + demands[j]).OnlyEnforceIf(x[i, j, v])
                    
    # Objective: Minimize total distance
    total_distance = sum(
        x[i, j, v] * distance_matrix[i][j] 
        for i in range(num_nodes) 
        for j in range(num_nodes) 
        for v in range(num_vehicles)
    )
    model.Minimize(total_distance)
    
    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        routes = []
        vehicle_distances = []
        vehicle_loads = []
        total_dist_val = 0
        
        for v in range(num_vehicles):
            route = [depot]
            curr = depot
            route_dist = 0
            route_load = 0
            while True:
                # find next node
                next_node = None
                for j in range(num_nodes):
                    if solver.Value(x[curr, j, v]) == 1:
                        next_node = j
                        break
                
                if next_node is None:
                    break
                    
                route.append(next_node)
                route_dist += distance_matrix[curr][next_node]
                route_load += demands[next_node]
                
                if next_node == depot:
                    break
                curr = next_node
                
            routes.append(route)
            vehicle_distances.append(route_dist)
            vehicle_loads.append(route_load)
            total_dist_val += route_dist
            
        return {
            "routes": routes,
            "vehicle_distances": vehicle_distances,
            "total_distance": total_dist_val,
            "vehicle_loads": vehicle_loads,
            "success": True,
            "status_code": status
        }
    else:
        return {
            "success": False,
            "status_code": status
        }


def solve_cvrp_greedy(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Greedy solver for CVRP. 
    Builds routes by always going to the nearest unvisited node that fits in the truck's capacity.
    """
    num_nodes = data["nodes"]["total"]
    depot = data["nodes"]["depot"]
    num_vehicles = data["vehicles"]["count"]
    capacity = data["vehicles"]["capacity_per_vehicle"]
    demands = data["demands"]
    dist = data["distance_matrix"]
    
    unvisited = set(range(num_nodes))
    if depot in unvisited:
        unvisited.remove(depot)
    
    routes = []
    vehicle_distances = []
    vehicle_loads = []
    total_distance = 0
    
    for v in range(num_vehicles):
        route = [depot]
        curr = depot
        curr_load = 0
        curr_dist = 0
        
        while unvisited:
            best_node = None
            best_d = float('inf')
            
            # Find nearest unvisited node that fits the remaining capacity
            for node in unvisited:
                if curr_load + demands[node] <= capacity:
                    if dist[curr][node] < best_d:
                        best_d = dist[curr][node]
                        best_node = node
                        
            if best_node is None:
                # No remaining unvisited nodes can fit inside this vehicle's capacity
                break
                
            # Move to best_node
            route.append(best_node)
            curr_dist += best_d
            curr_load += demands[best_node]
            unvisited.remove(best_node)
            curr = best_node
            
        # Return to depot
        route.append(depot)
        curr_dist += dist[curr][depot]
        
        routes.append(route)
        vehicle_distances.append(curr_dist)
        vehicle_loads.append(curr_load)
        total_distance += curr_dist
        
        if not unvisited:
            break
            
    # If there are empty vehicles left, add their default empty routes
    while len(routes) < num_vehicles:
        routes.append([depot, depot])
        vehicle_distances.append(dist[depot][depot])
        vehicle_loads.append(0)
        
    # Check if all nodes were successfully visited
    success = len(unvisited) == 0
    
    return {
        "routes": routes,
        "vehicle_distances": vehicle_distances,
        "total_distance": total_distance,
        "vehicle_loads": vehicle_loads,
        "success": success
    }


def solve_cvrp_greedy_parallel(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Greedy solver for CVRP. 
    Builds routes by always going to the nearest unvisited node that fits in the truck's capacity.
    """
    num_nodes = data["nodes"]["total"]
    depot = data["nodes"]["depot"]
    num_vehicles = data["vehicles"]["count"]
    capacity = data["vehicles"]["capacity_per_vehicle"]
    demands = data["demands"]
    dist = data["distance_matrix"]
    
    unvisited = set(range(num_nodes))
    if depot in unvisited:
        unvisited.remove(depot)
    
    routes = [[]]*num_vehicles
    vehicle_distances = [0]*num_vehicles
    vehicle_loads = [0]*num_vehicles
    position = [0]*num_vehicles #Current position of each vehicle
    total_distance = 0
    
    for v in range(num_vehicles):
        routes[v]= [depot]
        vehicle_distances[v]= 0
        vehicle_loads[v]= 0
        position[v]= depot
      

    while unvisited:
        best_node = None
        best_d = float('inf')

        #Select the vehicle with less current load
        if vehicle_loads[0] <= vehicle_loads[1]:
            v = 0 
        else:
            v = 1
        
        # Find nearest unvisited node that fits the remaining capacity
        for node in unvisited:
            if vehicle_loads[v] + demands[node] <= capacity:
                if dist[position[v]][node] < best_d:
                    best_d = dist[position[v]][node]
                    best_node = node
                    
        if best_node is None:
            # No remaining unvisited nodes can fit inside this vehicle's capacity
            break
            
        # Move to best_node
        routes[v].append(best_node)
        vehicle_distances[v] += best_d
        vehicle_loads[v] += demands[best_node]
        unvisited.remove(best_node)
        position[v] = best_node
        
    
        if not unvisited:
            break
    
    # Return to depot
    for v in range(num_vehicles):
        routes[v].append(depot)
        vehicle_distances[v] += dist[position[v]][depot]
        total_distance += vehicle_distances[v]

            
    # If there are empty vehicles left, add their default empty routes
    while len(routes) < num_vehicles:
        routes.append([depot, depot])
        vehicle_distances.append(dist[depot][depot])
        vehicle_loads.append(0)
        
    # Check if all nodes were successfully visited
    success = len(unvisited) == 0
    
    return {
        "routes": routes,
        "vehicle_distances": vehicle_distances,
        "total_distance": total_distance,
        "vehicle_loads": vehicle_loads,
        "success": success
    }
