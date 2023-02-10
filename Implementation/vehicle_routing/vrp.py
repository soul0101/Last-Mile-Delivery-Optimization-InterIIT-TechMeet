import os
import time
import json
import constants
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import shapefile as shp 
import vehicle_routing.helper as helper
import streamlit as st
from vehicle_routing.customers import Customers
from vehicle_routing.vehicle import Fleet
from shapely.geometry import Point, LineString
from vehicle_routing.route import Route, RoutesList
from ortools.constraint_solver import pywrapcp
from vehicle_routing.city_graph import CityGraph
from ortools.constraint_solver import routing_enums_pb2

class VRP:
    """
       The main solver class for solving the VRP problem.
       This class is used to solve the Vehicle Routing Problem (VRP) using the Google OR-Tools library. 
       It takes a depot location, a list of orders to be serviced, and a list of available vehicles as input, 
       and generates a set of optimized routes for the vehicles to follow in order to service all orders.

        Attributes:
        -----------
        depot: Depot
            The Depot class object from which vehicles will be dispatched.
        orders: List[Order]
            A list of orders to be serviced by the vehicles.
        vehicles: List[Vehicle]
            A list of indexes of vehicles available for servicing orders.
        customers: Customers
            A Customers class to store and process customer information
        fleet: Fleet
            The Fleet class represents a collection of vehicles and their properties
        routes_list: RoutesList
            The list of routes (route object) generated by the solver.

        Methods:
        -----------
        add_dynamic_order(new_order: Order) -> None: Add orders dynamically.
        get_routes() -> Dict[int, Route]: Returns the list of routes generated by the solver.
        update_routed_order_status(manager: RoutingIndexManager, routing: RoutingModel, solution: Assignment) -> None: Set the status of each order after the routing is completed.
        build_vehicle_routes(manager: RoutingIndexManager, routing: RoutingModel, solution: Assignment) -> None: Build the routes for each vehicle using the solution generated by the solver.
        vehicle_output_plot(block: Optional[bool] = True) -> None: Plot the routes for each vehicle on a map.
    """
    
    def __init__(self, depot, orders=None, vehicles=None):
        self.depot = depot
        self.orders = orders
        self.vehicles = vehicles  
        self.customers = None
        self.fleet = None   
        self.routes_list = None

    def add_dynamic_order(self, new_order):
        self.orders.append(new_order)

    def get_routes(self):
        return self.routes_list.routes_list

    def update_routed_order_status(self, manager, routing, solution):
        for order in range(routing.Size()):
            if (solution.Value(routing.NextVar(order)) == order):
                self.customers.customers[order].update_order_status(1)

        for vehicle_idx in range(self.fleet.num_vehicles):
            veh_used = routing.IsVehicleUsed(solution, vehicle_idx)

            if veh_used:
                node = routing.Start(vehicle_idx)  # Get the starting node index
                while not routing.IsEnd(node):
                    self.customers.customers[manager.IndexToNode(node)].status = 2
                    node = solution.Value(routing.NextVar(node))
                self.customers.customers[manager.IndexToNode(node)].status = 2                     

    def build_vehicle_routes(self, manager, routing, solution):
        routes_list = {}
        time_dimension = routing.GetDimensionOrDie('Time')

        for vehicle_idx in range(self.fleet.num_vehicles):
            veh_used = routing.IsVehicleUsed(solution, vehicle_idx)

            if veh_used:
                cur_route = []
                node = routing.Start(vehicle_idx)  # Get the starting node index
                while not routing.IsEnd(node):
                    time_val = solution.Min(time_dimension.CumulVar(node))
                    
                    current_order_object = self.customers.customers[manager.IndexToNode(node)]
                    current_order_object.predicted_time = time_val
                    print(time_val)
                    current_order_object.routing_time = time.time()

                    cur_route.append(current_order_object)
                    node = solution.Value(routing.NextVar(node))
                cur_route.append(self.customers.customers[manager.IndexToNode(node)])

                for customer in cur_route:
                    customer.vehicle = self.fleet.vehicle_list[vehicle_idx]

                routes_list[vehicle_idx] = Route(cur_route, self.vehicles[vehicle_idx])
            else:
                routes_list[vehicle_idx] = -1
            
            self.fleet.vehicle_list[vehicle_idx].route = routes_list[vehicle_idx]
        
        self.routes_list = RoutesList(routes_list)

    def vehicle_output_plot_routes(self, block=True, city_graph=False):
        if city_graph is True:
            self.city_graph.city.plot(facecolor="lightgrey", edgecolor="grey", linewidth=0.3)

        sf = shp.Reader(os.path.join(os.path.dirname(__file__), '../shapefile/test.shp'))
        for shape in sf.shapeRecords():
            y = [i[0] for i in shape.shape.points[:]]
            x = [i[1] for i in shape.shape.points[:]]
            plt.plot(y,x)

        plt.scatter(self.depot.lon, self.depot.lat, color='black', s=70, label='Depot')

        colors = ['red', 'blue', 'green', 'purple', 'darkblue', 'orange', 'brown', 'pink', 'olive', 'purple', 'tomato']
        for vehicle_idx, route in self.get_routes().items():
            if route == -1:
                continue

            x_coords = []
            y_coords = []

            for n in route.route:
                x_coords.append(n.lon)
                y_coords.append(n.lat)
            plt.scatter(x_coords[1:-1], y_coords[1:-1], color=colors[0], s=10)
            # plt.scatter(x_coords[1:-1], y_coords[1:-1], color=colors[vehicle_idx % len(colors)], s=10)
            # plt.plot(x_coords[1:-1], y_coords[1:-1], color=colors[vehicle_idx % len(colors)])
            # plt.plot(x_coords[:2], y_coords[:2], color=colors[vehicle_idx % len(colors)], linestyle='--', linewidth=1)
            # plt.plot(x_coords[-2:], y_coords[-2:], color=colors[vehicle_idx % len(colors)], linestyle='--', linewidth=1)
            
        plt.title('Vehicle Routes')
        plt.legend()
        plt.grid()
        plt.savefig(os.path.join(os.path.dirname(__file__), '..\plots\osrm_routes.png'), dpi=300)
        plt.show(block=block)

    def vehicle_return_plot_routes(self, block=True, city_graph=False):
        fig, ax = plt.subplots()
        if city_graph is True:
            self.city_graph.city.plot(facecolor="lightgrey", edgecolor="grey", linewidth=0.3, ax=ax)
            print('city printed')

        sf = shp.Reader(os.path.join(os.path.dirname(__file__), '../shapefile/test.shp'))
        
        for shape in sf.shapeRecords():
            y = [i[0] for i in shape.shape.points[:]]
            x = [i[1] for i in shape.shape.points[:]]
            ax.plot(y,x)

        ax.scatter(self.depot.lon, self.depot.lat, color='black', s=70, label='Depot')

        colors = ['red', 'blue', 'green', 'purple', 'darkblue', 'orange', 'brown', 'pink', 'olive', 'purple', 'tomato']
        for vehicle_idx, route in self.get_routes().items():
            if route == -1:
                continue

            x_coords = []
            y_coords = []

            for n in route.route:
                x_coords.append(n.lon)
                y_coords.append(n.lat)
            ax.scatter(x_coords[1:-1], y_coords[1:-1], color=colors[0], s=10)
            # plt.scatter(x_coords[1:-1], y_coords[1:-1], color=colors[vehicle_idx % len(colors)], s=10)
            # plt.plot(x_coords[1:-1], y_coords[1:-1], color=colors[vehicle_idx % len(colors)])
            # plt.plot(x_coords[:2], y_coords[:2], color=colors[vehicle_idx % len(colors)], linestyle='--', linewidth=1)
            # plt.plot(x_coords[-2:], y_coords[-2:], color=colors[vehicle_idx % len(colors)], linestyle='--', linewidth=1)
            
        ax.set_title('Vehicle Routes')
        ax.legend()
        ax.grid()
        # plt.savefig(os.path.join(os.path.dirname(__file__), '../plots/osrm_routes.png'), dpi=300)
        return fig

    def vehicle_return_plot(self, block=True, city_graph=False):
        fig, ax = plt.subplots()
        if city_graph is True:
            self.city_graph.city.plot(facecolor="lightgrey", edgecolor="grey", linewidth=0.3, ax=ax)

        s_del_lon = []
        s_del_lat = []
        s_pick_lon = []
        s_pick_lat = []

        for order in self.customers.orders:
            if order.type == 1:
                s_del_lon.append(order.lon)
                s_del_lat.append(order.lat)
            else:
                s_pick_lon.append(order.lon)
                s_pick_lat.append(order.lat)

            # plt.text(order.lon, order.lat, order.current_vrp_index, fontsize = 8)

        ax.scatter(s_del_lon, s_del_lat, color='b', label='Delivery', s=20)
        ax.scatter(s_pick_lon, s_pick_lat, color='g', label='Pickup', s=20)
        ax.scatter(self.depot.lon, self.depot.lat, color='black', s=70, label='Depot')

        for vehicle_idx, route in self.get_routes().items():
            if route == -1:
                continue

            lon_coords = []
            lat_coords = []

            for n in route.route:
                lon_coords.append(n.lon)
                lat_coords.append(n.lat)
            ax.plot(lon_coords, lat_coords)
            
        ax.set_title('Routes')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.legend()
        # ax.show(block=block)
        # ax.figure()
        return fig

    def vehicle_output_plot(self, block=True, city_graph=False):
        if city_graph is True:
            self.city_graph.city.plot(facecolor="lightgrey", edgecolor="grey", linewidth=0.3)

        s_del_lon = []
        s_del_lat = []
        s_pick_lon = []
        s_pick_lat = []

        for order in self.customers.orders:
            if order.type == 1:
                s_del_lon.append(order.lon)
                s_del_lat.append(order.lat)
            else:
                s_pick_lon.append(order.lon)
                s_pick_lat.append(order.lat)

            # plt.text(order.lon, order.lat, order.current_vrp_index, fontsize = 8)

        plt.scatter(s_del_lon, s_del_lat, color='b', label='Delivery', s=20)
        plt.scatter(s_pick_lon, s_pick_lat, color='g', label='Pickup', s=20)
        plt.scatter(self.depot.lon, self.depot.lat, color='black', s=70, label='Depot')

        for vehicle_idx, route in self.get_routes().items():
            if route == -1:
                continue

            lon_coords = []
            lat_coords = []

            for n in route.route:
                lon_coords.append(n.lon)
                lat_coords.append(n.lat)
            plt.plot(lon_coords, lat_coords)
            
        plt.title('Routes')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.legend()
        plt.show(block=block)
        plt.figure()

    @helper.timer_func
    def process_VRP(self, isReroute=False, centrality_check=False, edge_weight_type='haversine',
            time_limit=300, total_transit_time = 10_000_000, max_wait_time=10_000, 
            max_route_distance=2000_000, equalize_routes=False, equalize_routes_penalty=10_000,
            first_sol_strategy="AUTOMATIC", initial_metaheuristic="AUTOMATIC", rerouting_metaheuristic="AUTOMATIC"):

        self.fleet = Fleet(self.vehicles)
        self.customers = Customers(self.depot, self.orders)
        self.fleet.set_starts_ends()
        self.city_graph = CityGraph(self.customers.orders)

        if centrality_check:
            self.priorities = self.city_graph.get_priorities()

        # for order in self.customers.orders:
        #     print(order.priority, order.deadline, order.carryforward_penalty)
        """
        PROBLEM SETUP
        -------------
        """
        #Create the routing index manager
        manager = pywrapcp.RoutingIndexManager(
            self.customers.number,  # int number
            self.fleet.num_vehicles,  # int number
            self.fleet.starts,  # List of int start depot
            self.fleet.ends)  # List of int end depot

        self.customers.set_manager(manager)

        #Create Routing Model
        routing = pywrapcp.RoutingModel(manager)

        # Create callback fns for distances.
        dist_fn = self.customers.return_dist_callback(method=edge_weight_type)
        dist_fn_index = routing.RegisterTransitCallback(dist_fn)
        routing.SetArcCostEvaluatorOfAllVehicles(dist_fn_index)

        routing.AddDimension(
            dist_fn_index,  # total distance function callback
            0, 
            max_route_distance,
            True,
            'Distance')
        distance_dimension = routing.GetDimensionOrDie('Distance')
        
        # if global_span_coefficient is not None:
        #     distance_dimension.SetGlobalSpanCostCoefficient(global_span_coefficient)

        if equalize_routes:
            routing.AddConstantDimension(
                1, # increment by one every time
                self.customers.number, # large enough
                True,  # set count to zero
            'Count')

            count_dimension = routing.GetDimensionOrDie('Count')
            count_dimension.SetGlobalSpanCostCoefficient(equalize_routes_penalty)

            # Add penalty if vehicle serve too much nodes
            for v in range(manager.GetNumberOfVehicles()):
                end = routing.End(v)
                count_dimension.SetCumulVarSoftUpperBound(
                    end, # index
                    (self.customers.number - 1) // self.fleet.num_vehicles + 1, # soft max
                    equalize_routes_penalty # penalty
                )

        print(
            self.customers.number,  # int number
            self.fleet.num_vehicles,  # int number
            self.fleet.starts,  # List of int start depot
            self.fleet.ends, 
            self.fleet.capacities)

        # Create callback fns for service and transit-times.
        serv_time_fn = self.customers.make_service_time_call_callback()
        transit_time_fn = self.customers.make_transit_time_callback()

        def tot_time_fn(from_index, to_index):
            """
            The time function we want is both transit time and service time.
            """
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return serv_time_fn(from_node, to_node) + transit_time_fn(from_node, to_node)

        tot_time_fn_index = routing.RegisterTransitCallback(tot_time_fn)
        routing.AddDimension(
            tot_time_fn_index,  # total time function callback
            max_wait_time, 
            total_transit_time,
            True,
            'Time')

        time_dimension = routing.GetDimensionOrDie('Time')

        # Add time window constraints for each location except depot.
        for order in self.customers.orders:
            if order.type == 1 and order.start_time and order.end_time:
                index = manager.NodeToIndex(order.current_vrp_index)
                time_dimension.CumulVar(index).SetRange(order.start_time, order.end_time)

        # Instantiate route start and end times to produce feasible times.

        for vehicle_idx in range(self.fleet.num_vehicles):
            routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.Start(vehicle_idx)))
            routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(vehicle_idx)))

        delivery_fn = self.customers.return_delivery_callback()
        delivery_fn_index = routing.RegisterUnaryTransitCallback(delivery_fn)

        load_fn = self.customers.return_load_callback()
        load_fn_index = routing.RegisterUnaryTransitCallback(load_fn)

        routing.AddDimensionWithVehicleCapacity(
            delivery_fn_index,
            0,  # null capacity slack
            self.fleet.capacities,  # vehicle maximum capacities
            False,  # start cumul to zero
        'Deliveries')
        
        routing.AddDimensionWithVehicleCapacity(
            load_fn_index,
            0,  # null capacity slack
            self.fleet.capacities,  # vehicle maximum capacities
            False,  # start cumul to zero
        'Loads')

        # Add Constraint Both cumulVar are identical at start
        deliveries_dimension = routing.GetDimensionOrDie('Deliveries')
        loads_dimension = routing.GetDimensionOrDie('Loads')
        for vehicle_id in range(self.fleet.num_vehicles):
            index = routing.Start(vehicle_id)
            routing.solver().Add(deliveries_dimension.CumulVar(index) == loads_dimension.CumulVar(index))

        for node in range(1, self.customers.number):
            routing.AddDisjunction([manager.NodeToIndex(node)], int(self.customers.customers[node].carryforward_penalty))

        """
        SETTING PARAMETERS
        ------------------
        """
        parameters = pywrapcp.DefaultRoutingSearchParameters()
        parameters.first_solution_strategy = (helper.get_first_sol_strategy(first_sol_strategy))
        parameters.local_search_metaheuristic = (helper.get_local_search_metaheuristic(initial_metaheuristic))

        # Routing: forbids use of TSPOpt neighborhood, (this is the default behaviour)
        # parameters.local_search_operators.use_tsp_opt = pywrapcp.BOOL_FALSE
        # Disabling Large Neighborhood Search, (this is the default behaviour)
        # parameters.local_search_operators.use_path_lns = pywrapcp.BOOL_FALSE
        # parameters.local_search_operators.use_inactive_lns = pywrapcp.BOOL_FALSE
    
        parameters.time_limit.FromSeconds(time_limit)
        # parameters.use_full_propagation = True    

        if isReroute: 
            parameters.local_search_metaheuristic = (helper.get_local_search_metaheuristic(rerouting_metaheuristic))

            for i, order in enumerate(self.customers.orders): 
                if order.status == 2 and order.type == 1:
                    routing.VehicleVar(manager.NodeToIndex(i+1)).SetValues([order.vehicle.vehicle_index])

            routing.CloseModelWithParameters(parameters)

            curr_solution = self.routes_list.get_initial_routes()
            print(curr_solution)
            initial_solution = routing.ReadAssignmentFromRoutes(curr_solution,True)
            solution = routing.SolveFromAssignmentWithParameters( initial_solution, parameters)
            # solution = routing.SolveWithParameters(parameters)
        
        else:
            solution = routing.SolveWithParameters(parameters)

        if solution: 
            self.update_routed_order_status(manager, routing, solution)
            self.build_vehicle_routes(manager, routing, solution)
            return manager, routing, solution
        else:
            print("NO SOLUTION FOUND")
            return None

    def export_shapefile(self):
        all_route_coords = []
        all_route_awbs = []

        route_list = self.get_routes()
        for route_index, route_obj in route_list.items():
            route_coords= []
            route_awb = []
            if route_obj == -1:
                continue
            for order in route_obj.route:
                route_coords.append(order.coordinates)
                if order.type == 0:
                    continue
                route_awb.append([order.AWB, order.coordinates])
                    
            all_route_coords.append(route_coords)
            all_route_awbs.append(route_awb)

        # print(all_route_coords)
        # print(all_route_awbs)

        geo_routes = []
        data = pd.DataFrame({'Route': [str(i+1) for i in range(len(all_route_coords))]})
        #http://router.project-osrm.org/route/v1/driving/77.586607,12.909694;77.652492,12.91763?overview=full&geometries=geojson
        # osrm_url_base = "https://routing.openstreetmap.de/routed-bike/route/v1/driving/"
        osrm_url_base = constants.OSRM_BASE_URL + "route/v1/driving/"

        for route in all_route_coords:
            points_list = []
            for point in route:
                points_list.append(str(point[1])  + "," + str(point[0]))
            osrm_url = osrm_url_base + ";".join(points_list) + "?overview=full&geometries=geojson"
            r = requests.get(osrm_url)
            t = json.loads(r.text)
            coordinates = t['routes'][0]['geometry']['coordinates']
            points_list = []
            for point in coordinates:
                points_list.append(Point(point[0], point[1]))
            geo_routes.append(LineString(points_list))

        myGDF = gpd.GeoDataFrame(data, geometry=geo_routes)
        # myGDF.to_file(filename='myshapefile_test.shp.zip', driver='ESRI Shapefile')
        myGDF.to_file(os.path.join(os.path.dirname(__file__), '../shapefile/test.shp'), mode='w')

