import math
import helper
import random 
import numpy as np
from sklearn.metrics import pairwise
from ortools.constraint_solver import pywrapcp

import matplotlib.pyplot as plt

def generate_locs(num_rows):
    lat = 31.156412
    lon = 121.271469

    result = []

    for _ in range(num_rows):
        dec_lat = random.random()/100
        dec_lon = random.random()/100

        result.append([lat + dec_lat, lon + dec_lon])
        
    return result

def create_data_model(input_locations, vehicle_capacities, deliveries, loads):
    assert (len(vehicle_capacities) > 0), "Number of vehicles have to be greater than 0"

    """Stores the data_model for the problem."""
    data_model = {}
    data_model['distance_matrix'] = []
    input_locations = [[math.radians(float(_[0])), math.radians(float(_[1]))] for _ in input_locations]
    data_model['distance_matrix'] = np.ceil(pairwise.haversine_distances(input_locations) * 637100)
    
    num_drops = len(input_locations) - 1
    num_vehicles = len(vehicle_capacities)
    data_model['demands'] = np.ones(num_drops + 1)
    data_model['demands'][0] = 0
    data_model['vehicle_capacities'] = vehicle_capacities
    data_model['num_vehicles'] = num_vehicles
    data_model['depot'] = 0
    data_model['num_drops'] = num_drops
    data_model['deliveries'] = deliveries
    data_model['loads'] = loads

    return data_model

def optimizer(input_locations, vehicle_capacities, deliveries, loads, carryforward_penalty=1000, search_timeout=3000, 
                    first_sol_strategy="AUTOMATIC",
                    ls_metaheuristic="AUTOMATIC"):

    data_model = create_data_model(input_data, vehicle_capacities, deliveries, loads)

    #Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(len(data_model['distance_matrix']),
                                           data_model['num_vehicles'], data_model['depot'])


    #Create Routing Model
    routing = pywrapcp.RoutingModel(manager)


    #Create and register a transit callback
    def distance_callback(from_index, to_index):
        """
        Returns the distance between the two nodes
        Convert from routing variable Index to distance matrix NodeIndex.
        """
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data_model['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    #Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Deliveries constraint.
    def delivery_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data_model['deliveries'][from_node]
    delivery_callback_index = routing.RegisterUnaryTransitCallback(delivery_callback)
    routing.AddDimensionWithVehicleCapacity(
        delivery_callback_index,
        0,  # null capacity slack
        data_model['vehicle_capacities'],  # vehicle maximum capacities
        False,  # start cumul to zero
        'Deliveries')

    # Add Load constraint.
    def load_callback(from_index):
        """Returns the load of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data_model['loads'][from_node]
    load_callback_index = routing.RegisterUnaryTransitCallback(load_callback)
    routing.AddDimensionWithVehicleCapacity(
        load_callback_index,
        0,  # null capacity slack
        data_model['vehicle_capacities'],  # vehicle maximum capacities
        False,  # start cumul to zero
        'Loads')

    # Add Constraint Both cumulVar are identical at start
    deliveries_dimension = routing.GetDimensionOrDie('Deliveries')
    loads_dimension = routing.GetDimensionOrDie('Loads')
    for vehicle_id in range(data_model['num_vehicles']):
      index = routing.Start(vehicle_id)
      routing.solver().Add(
          deliveries_dimension.CumulVar(index) == loads_dimension.CumulVar(index))

    # penalty = carryforward_penalty          # Penalty for not delivering to a drop point
    # for node in range(1, len(data_model['distance_matrix'])):
    #     routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    #Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (helper.get_first_sol_strategy(first_sol_strategy))
    search_parameters.local_search_metaheuristic = (helper.get_local_search_metaheuristic(ls_metaheuristic))
    search_parameters.time_limit.FromSeconds(search_timeout)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        return helper.print_solution(data_model, manager, routing, solution, input_locations)
    else:
        return "No Solution"

if __name__ == '__main__':
    tot_locs = 100
    input_data = generate_locs(tot_locs)

    # Hard code vehicle capacities
    vehicle_capacities = 20 * np.ones(math.ceil((tot_locs - 1) / 20))

    num_locs = len(input_data) - 1

    # Number of deliveries v/s pickups (RNG)
    # https://stackoverflow.com/questions/67000884/google-or-tools-vrp-pickup-dropoff-at-same-node

    num_dels = random.randrange(num_locs)
    deliveries = np.concatenate([np.array([0]), -1*np.ones(num_dels), np.zeros(num_locs - num_dels)])
    loads = np.concatenate([np.array([0]), -1*np.ones(num_dels), np.ones(num_locs - num_dels)])

    data = optimizer(input_data, vehicle_capacities, deliveries, loads, carryforward_penalty=1000000, search_timeout=600)
    for route_id, route_data in data.items():
        # Extract the x and y coordinates for the route
        x_coords = route_data['route_locs_x']
        y_coords = route_data['route_locs_y']

        # Plot the route using the x and y coordinates
        plt.plot(x_coords, y_coords)

        # Plot the Points
        lons, lats = zip(*input_data)

        depot_lat = lats[0]
        depot_lon = lons[0]
        plt.scatter([depot_lon], [depot_lat], color='red', label='Depot')

        deliver_lats = lats[1:num_dels+1]
        deliver_lons = lons[1:num_dels+1]
        plt.scatter(deliver_lons, deliver_lats, color='blue', label='Deliveries')

        pickup_lats = lats[1+num_dels:]
        pickup_lons = lons[1+num_dels:]
        plt.scatter(pickup_lons, pickup_lats, color='green', label="Pick-Ups")

    # Add a title and axis labels
    plt.title('Routes')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Show the plot
    plt.show()
    