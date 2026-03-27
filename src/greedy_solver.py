from typing import Dict, Any

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
