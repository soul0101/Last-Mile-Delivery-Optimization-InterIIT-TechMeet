from ortools.constraint_solver import routing_enums_pb2

def print_solution(data_model, manager, routing, solution, input_locations):
    total_distance = 0
    total_load = 0
    final_route = {}

    for vehicle_id in range(data_model['num_vehicles']):
        if data_model['num_drops'] <= vehicle_id:
            continue
        index = routing.Start(vehicle_id)
        route_distance = 0
        route_load = 0

        route_locs_x = []
        route_locs_y = []
        route_node_index = []
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)

            route_locs_x.append(input_locations[node_index][0])
            route_locs_y.append(input_locations[node_index][1])
            route_node_index.append(node_index)

            route_load += data_model['demands'][node_index]
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)

        route_locs_x.append(route_locs_x[0])
        route_locs_y.append(route_locs_y[0])
        route_node_index.append(route_node_index[0])

        total_distance += route_distance
        total_load += route_load
        final_route[vehicle_id] = {
            "route_locs_x": route_locs_x,
            "route_locs_y": route_locs_y,
            "route_node_index": route_node_index
        }

    return final_route
    
def get_local_search_metaheuristic(local_mh):
    pick_local_search_metaheuristic = {
        "AUTOMATIC": routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC,
        "GREEDY_DESCENT": routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT, 
        "GUIDED_LOCAL_SEARCH": routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
        "SIMULATED_ANNEALING": routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING, 
        "TABU_SEARCH" : routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH
    }
    return pick_local_search_metaheuristic[local_mh]

def get_first_sol_strategy(first_sol_strategy):
    pick_first_sol = {
        "AUTOMATIC" : routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC, 
        "PATH_CHEAPEST_ARC" : routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC, 
        "PATH_MOST_CONSTRAINED_ARC" : routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC, 
        "EVALUATOR_STRATEGY" : routing_enums_pb2.FirstSolutionStrategy.EVALUATOR_STRATEGY, 
        "SAVINGS" : routing_enums_pb2.FirstSolutionStrategy.SAVINGS, 
        "SWEEP" : routing_enums_pb2.FirstSolutionStrategy.SWEEP, 
        "CHRISTOFIDES" : routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES, 
        "ALL_UNPERFORMED" : routing_enums_pb2.FirstSolutionStrategy.ALL_UNPERFORMED,
        "BEST_INSERTION" : routing_enums_pb2.FirstSolutionStrategy.BEST_INSERTION, 
        "PARALLEL_CHEAPEST_INSERTION" : routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION, 
        "LOCAL_CHEAPEST_INSERTION" : routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION,
        "GLOBAL_CHEAPEST_ARC" : routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC, 
        "LOCAL_CHEAPEST_ARC" : routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_ARC, 
        "FIRST_UNBOUND_MIN_VALUE" : routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE
    }

    return pick_first_sol[first_sol_strategy]