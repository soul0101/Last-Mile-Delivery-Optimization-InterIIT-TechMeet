import math
import random 
import numpy as np
from sklearn.metrics import pairwise
from datetime import datetime, timedelta
from ortools.constraint_solver import pywrapcp
from vehicle_routing.customers import Node, Order
from vehicle_routing.vehicle import Vehicle
from vehicle_routing.vrp import VRP 

#ToDo: after all routes generated update status 
# Time intervals, also maintain current time

def generate_locs(num_rows):
    lat = 31.156412
    lon = 121.271469

    result = []

    for _ in range(num_rows):
        dec_lat = random.random()/100
        dec_lon = random.random()/100

        result.append([lat + dec_lat, lon + dec_lon])
    
    return np.array(result)

def generate_random_problem(num_orders=50):
    def generate_coordinates(center_lat, center_long, radius=27000):
        radius_in_degrees = radius / 111300
        u = random.uniform(0, 1)
        v = random.uniform(0, 1)
        w = radius_in_degrees * math.sqrt(u)
        t = 2 * math.pi * v
        x = w * math.cos(t)
        y = w * math.sin(t)
        new_x = x / math.cos(math.radians(center_lat))
        new_long = new_x + center_long
        new_lat = y + center_lat
        return [new_lat, new_long]
        
    depot = Node([12.9716, 77.5946], 0)
    orders = []
    vehicles = []

    for i in range(num_orders):
        orders.append(Order(1, generate_coordinates(12.9716, 77.5946), np.random.choice([1, 2], size=1, p=[0.7, 0.3])))
    
    num_vehicles = num_orders // 20
    for i in range(num_vehicles):
        vehicles.append(Vehicle(25, start=depot, end=depot))
    
    print(len(orders), len(vehicles))
    return depot, orders, vehicles

def vehicle_output_string(manager, routing, plan):
    """
    Return a string displaying the output of the routing instance and
    assignment (plan).
    Args: routing (ortools.constraint_solver.pywrapcp.RoutingModel): routing.
    plan (ortools.constraint_solver.pywrapcp.Assignment): the assignment.
    Returns:
        (string) plan_output: describing each vehicle's plan.
        (List) dropped: list of dropped orders.
    """
    print('The Objective Value is {0}'.format(plan.ObjectiveValue()))
    dropped = []
    for order in range(routing.Size()):
        if (plan.Value(routing.NextVar(order)) == order):
            dropped.append(str(order))

    deliveries_dimension = routing.GetDimensionOrDie('Deliveries')
    loads_dimension = routing.GetDimensionOrDie('Loads')
    time_dimension = routing.GetDimensionOrDie('Time')
    plan_output = ''

    for route_number in range(routing.vehicles()):
        order = routing.Start(route_number)
        plan_output += 'Route {0}:'.format(route_number)
        if routing.IsEnd(plan.Value(routing.NextVar(order))):
            plan_output += ' Empty \n'
        else:
            while True:
                load_var = loads_dimension.CumulVar(order)
                delivery_var = deliveries_dimension.CumulVar(order)
                time_var = time_dimension.CumulVar(order)
                node = manager.IndexToNode(order)
                plan_output += \
                    ' {node} Load({load}) Delivery({delivery}) Time({tmin}, {tmax}) -> '.format(
                        node=node,
                        delivery=plan.Value(delivery_var),
                        load=plan.Value(load_var),
                        tmin=str(timedelta(seconds=plan.Min(time_var))),
                        tmax=str(timedelta(seconds=plan.Max(time_var))))
        #         plan_output += \
        #             ' {node} Load({load}) Delivery({delivery}) -> '.format(
        #                 node=node,
        #                 delivery=plan.Value(delivery_var),
        #                 load=plan.Value(load_var))

                if routing.IsEnd(order):
                    plan_output += ' EndRoute {0}. \n'.format(route_number)
                    break
                order = plan.Value(routing.NextVar(order))
        plan_output += '\n'

    return (plan_output, dropped)
    
if __name__ == '__main__':
    # depot = Node([0, 0], 0)
    # orders = [Order(1, [0, 1], 1), Order(1, [1, 0], 1), Order(1, [1, 4], 1), Order(1, [2, 5], 1), Order(1, [6, 9], 1), 
    #         Order(1, [5, 3], 2), Order(1, [3, 1], 2), Order(1, [1, 6], 2), Order(1, [-5, -3], 1), Order(1, [-1, -4], 1), Order(1, [-3, 2], 1)]
    # vehicles = [Vehicle(6, start=depot, end=depot), Vehicle(6, start=depot, end=depot), Vehicle(6, start=depot, end=depot), Vehicle(6, start=depot, end=depot)]
    # vehicles = [Vehicle(3, start=depot, end=depot)]
    
    depot, orders, vehicles = generate_random_problem(num_orders=80)

    vrp_instance = VRP(depot, orders, vehicles)
    manager, routing, solution = vrp_instance.process_VRP()

    plan_output, dropped = vehicle_output_string(manager, routing, solution)
    print(plan_output)
    print('dropped nodes: ' + ', '.join(dropped))
    # vrp_instance.vehicle_output_plot()

    vrp_instance.vehicle_output_plot(block=False)
    routes_list = vrp_instance.get_routes()
    routes_list[3].next_node(3)
    routes_list[3].next_node(3)
    routes_list[2].next_node(3)
    routes_list[2].next_node(3)
    routes_list[2].next_node(3)

    manager, routing, solution = vrp_instance.process_VRP(isReroute=True)
    vrp_instance.vehicle_output_plot()
    plan_output, dropped = vehicle_output_string(manager, routing, solution)
    print(plan_output)
    print('dropped nodes: ' + ', '.join(dropped))



    