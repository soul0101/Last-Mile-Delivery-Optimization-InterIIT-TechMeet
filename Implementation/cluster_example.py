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
    
    num_orders = len(orders)
    points_per_cluster = 50
    clusters = clustering.clustered(depot, orders, points_per_cluster)
    vehicles_per_cluster= math.ceil(len(vehicles)/len(clusters))
    all_routes=[]

    clustered_total_distance = 0
    for i in range(len(clusters)):
        subvrp_instance = VRP(depot, clusters[i], vehicles[i*vehicles_per_cluster: min((i+1)*vehicles_per_cluster, len(vehicles))]) #check for the case: if no of clusters not a factor of no of vehicles
        manager, routing, solution = subvrp_instance.process_VRP()
        plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
        clustered_total_distance += total_distance
        routes_list = subvrp_instance.get_routes()
        all_routes.append(routes_list)

    new_routes_list = {}
    i = 0
    for route in all_routes:
        for key, route in route.items():
            new_routes_list[i] = route
            i += 1

    print("clusterd total distance: ", clustered_total_distance)
    # manager, routing, solution = vrp_instance.process_VRP(edge_weight_type='osrm')
    # manager, routing, solution = vrp_instance.process_VRP(edge_weight_type='haversine')

    # plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
    # print(plan_output)
    # print('dropped nodes: ' + ', '.join(dropped))
    # print("Total Distance: ", total_distance)

    # vrp_instance.export_shapefile()
    # vrp_instance.vehicle_output_plot(block=False)
    # vrp_instance.vehicle_output_plot_routes(city_graph=True)
    # vrp_instance.routes_list.skip_time(30)
    # plan_output, dropped = vehicle_output_string(manager, routing, solution)
    # print(plan_output)
    # print('dropped nodes: ' + ', '.join(dropped))
    # vrp_instance.city_graph.city.plot(facecolor="lightgrey", edgecolor="grey", linewidth=0.3)
    # vrp_instance.vehicle_output_plot()

    # vrp_instance.vehicle_output_plot(block=False)

    vrp_instance=VRP(depot, orders, vehicles, RoutesList(new_routes_list))
    
    route_list = vrp_instance.routes_list
    for vehicle_idx, route in routes_list.items():
        if route == -1:
            continue
        for i in range(3):
            route.next_node(3)
    
    manager, routing, solution = vrp_instance.process_VRP(isReroute=True)
    vrp_instance.vehicle_output_plot()
    # vrp_instance.vehicle_output_plot()
    plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
    print(plan_output)
    print('dropped nodes: ' + ', '.join(dropped))
    print('Total Distance: ', total_distance)