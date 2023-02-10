import os
import copy
import math
import random 
import numpy as np
from datetime import timedelta
from vehicle_routing.vrp import VRP 
import vehicle_routing.helper as helper
from vehicle_routing.route import RoutesList
import vehicle_routing.clustering as clustering

if __name__ == '__main__':
    # depot, orders, vehicles = helper.generate_random_problem(num_orders=200)
    mock_dispatch_filename = os.path.dirname(__file__) + r'\mock\dispatch_testing.xlsx'
    mock_pickup_filename = os.path.dirname(__file__) + r'\mock\pickups_testing.xlsx'
    depot, orders, vehicles = helper.generate_problem_from_file(mock_dispatch_filename, mock_pickup_filename)
    vrp_instance = VRP(depot, orders, vehicles)
    
    # manager, routing, solution = vrp_instance.process_VRP(edge_weight_type='osrm')
    manager, routing, solution = vrp_instance.process_VRP(edge_weight_type='haversine')

    plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
    print(plan_output)
    print('dropped nodes: ' + ', '.join(dropped))
    print("Total Distance: ", total_distance)

    vrp_instance.export_shapefile()
    vrp_instance.vehicle_output_plot_routes()