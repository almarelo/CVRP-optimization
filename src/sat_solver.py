from ortools.sat.python import cp_model
from typing import Dict, Any

def solve_cvrp_sat(data: Dict[str, Any]) -> Dict[str, Any]:

    """
    Solves CVRP with OR-Tools CP-SAT solver.
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
