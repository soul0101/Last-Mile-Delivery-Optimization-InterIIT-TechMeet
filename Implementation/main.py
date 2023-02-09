import os
import math
import random 
import numpy as np

from vehicle_routing.vrp import VRP 
import vehicle_routing.helper as helper

from datetime import timedelta
    
if __name__ == '__main__':
    
    depot, orders, vehicles = helper.generate_random_problem(num_orders=20)
    # mock_dispatch_filename = os.path.dirname(__file__) + r'\mock\dispatch_testing.xlsx'
    # mock_pickup_filename = os.path.dirname(__file__) + r'\mock\pickups_testing.xlsx'
    # depot, orders, vehicles = helper.generate_problem_from_file(mock_dispatch_filename, mock_pickup_filename)
    vrp_instance = VRP(depot, orders, vehicles)

    # Check time window solution
    # new_order = helper.generate_random_order(type=1, start_time=14, end_time=25)
    # vrp_instance.add_dynamic_order(new_order)

    manager, routing, solution = vrp_instance.process_VRP()

    plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
    print(plan_output)
    print('dropped nodes: ' + ', '.join(dropped))
    print("Total Distance: ", total_distance)
    vrp_instance.city_graph.city.plot(facecolor="lightgrey", edgecolor="grey", linewidth=0.3)
    vrp_instance.vehicle_output_plot()
    vrp_instance.export_shapefile()
    
    # vrp_instance.vehicle_output_plot(block=False)
    # routes_list = vrp_instance.get_routes()
    
    # for vehicle_idx, route in routes_list.items():
    #     if route == -1:
    #         continue
    #     for i in range(3):
    #         route.next_node(3)

    # for i in range(5):
    #     vrp_instance.add_dynamic_order(helper.generate_random_order())
    
    # manager, routing, solution = vrp_instance.process_VRP(isReroute=True, rerouting_metaheuristic="AUTOMATIC", time_limit=20)
    # vrp_instance.vehicle_output_plot()
    # plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
    # print(plan_output)
    # print('dropped nodes: ' + ', '.join(dropped))
    # print('Total Distance: ', total_distance)



    