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
    mock_dispatch_filename = os.path.dirname(__file__) + r'\mock\dispatch_testing.xlsx'
    mock_pickup_filename = os.path.dirname(__file__) + r'\mock\pickups_testing.xlsx'
    depot, orders, vehicles = helper.generate_problem_from_file(mock_dispatch_filename, mock_pickup_filename)
    vrp_instance = VRP(depot, orders, vehicles)
    
    manager, routing, solution = vrp_instance.process_VRP(edge_weight_type='haversine')

    plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
    vrp_instance.vehicle_output_plot(block=False, city_graph=True)

    print(plan_output)
    print('dropped nodes: ' + ', '.join(dropped))
    print("Total Distance: ", total_distance)

    # Skip time by 30 minutes
    vrp_instance.routes_list.skip_time(30)
    
    # Add 5 Dynamic Pickups
    for i in range(5):
        vrp_instance.add_dynamic_order(helper.generate_random_order())
    
    # Dynamic Rerouting
    manager, routing, solution = vrp_instance.process_VRP(isReroute=True)

    vrp_instance.vehicle_output_plot(city_graph=True)
    plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
    print(plan_output)
    print('dropped nodes: ' + ', '.join(dropped))
    print('Total Distance: ', total_distance)