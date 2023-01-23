import matplotlib.pyplot as plt
from vehicle_routing.customers import Order, Customers
from vehicle_routing.vehicle import Vehicle, Fleet
from vehicle_routing.route import Route
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

class VRP:
    def __init__(self, depot, orders=None, vehicles=None):
        self.depot = depot
        self.orders = orders
        self.vehicles = vehicles  
        self.customers = None
        self.fleet = None   
        self.routes_list = None

    def get_routes(self):
        return self.routes_list

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

        for vehicle_idx in range(self.fleet.num_vehicles):
            veh_used = routing.IsVehicleUsed(solution, vehicle_idx)

            if veh_used:
                cur_route = []
                node = routing.Start(vehicle_idx)  # Get the starting node index
                while not routing.IsEnd(node):
                    cur_route.append(self.customers.customers[manager.IndexToNode(node)])
                    node = solution.Value(routing.NextVar(node))
                cur_route.append(self.customers.customers[manager.IndexToNode(node)])

                for customer in cur_route:
                    customer.vehicle = self.fleet.vehicle_list[vehicle_idx]

                routes_list[vehicle_idx] = Route(cur_route, self.vehicles[vehicle_idx])
            else:
                routes_list[vehicle_idx] = -1
            
            self.fleet.vehicle_list[vehicle_idx].route = routes_list[vehicle_idx]
        
        self.routes_list = routes_list

    def vehicle_output_plot(self, block=True):
        plt.figure()
        s_del_x = []
        s_del_y = []
        s_pick_x = []
        s_pick_y = []

        for order in self.customers.orders:
            if order.type == 1:
                s_del_x.append(order.lat)
                s_del_y.append(order.lon)
            else:
                s_pick_x.append(order.lat)
                s_pick_y.append(order.lon)

            plt.text(order.lat, order.lon, order.current_vrp_index, fontsize = 8)

        plt.scatter(s_del_x, s_del_y, color='b', label='Delivery')
        plt.scatter(s_pick_x, s_pick_y, color='g', label='Pickup')
        plt.scatter(self.depot.lat, self.depot.lon, color='black', s=70, label='Depot')

        for vehicle_idx, route in self.routes_list.items():
            if route == -1:
                continue

            x_coords = []
            y_coords = []

            for n in route.route:
                x_coords.append(n.lat)
                y_coords.append(n.lon)
            plt.plot(x_coords, y_coords)
            
        plt.title('Routes')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.legend()
        plt.show(block=block)

    def process_VRP(self, isReroute=False):
        self.fleet = Fleet(self.vehicles)
        self.customers = Customers(self.depot, self.orders)

        self.fleet.set_starts_ends()

        #Create the routing index manager
        manager = pywrapcp.RoutingIndexManager(
            self.customers.number,  # int number
            self.fleet.num_vehicles,  # int number
            self.fleet.starts,  # List of int start depot
            self.fleet.ends)  # List of int end depot

        self.customers.set_manager(manager)
        #Create Routing Model
        routing = pywrapcp.RoutingModel(manager)

        # Create callback fns for distances, demands, service and transit-times.
        dist_fn = self.customers.return_dist_callback(method='haversine')
        dist_fn_index = routing.RegisterTransitCallback(dist_fn)
        routing.SetArcCostEvaluatorOfAllVehicles(dist_fn_index)

        print(
            self.customers.number,  # int number
            self.fleet.num_vehicles,  # int number
            self.fleet.starts,  # List of int start depot
            self.fleet.ends, 
            self.fleet.capacities)

        # Create and register a transit callback.
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

        # total_transit_time = 360
        total_transit_time = 10000000
        tot_time_fn_index = routing.RegisterTransitCallback(tot_time_fn)
        routing.AddDimension(
            tot_time_fn_index,  # total time function callback
            0, 
            total_transit_time,
            True,
            'Time')

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
            routing.AddDisjunction([manager.NodeToIndex(node)], self.customers.customers[node].carryforward_penalty)

        parameters = pywrapcp.DefaultRoutingSearchParameters()
        # Setting first solution heuristic (cheapest addition).
        parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)
        parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC)
        # parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH)

        # Routing: forbids use of TSPOpt neighborhood, (this is the default behaviour)
        # parameters.local_search_operators.use_tsp_opt = pywrapcp.BOOL_FALSE
        # Disabling Large Neighborhood Search, (this is the default behaviour)
        # parameters.local_search_operators.use_path_lns = pywrapcp.BOOL_FALSE
        # parameters.local_search_operators.use_inactive_lns = pywrapcp.BOOL_FALSE
    
        parameters.time_limit.FromSeconds(300)
        # parameters.use_full_propagation = True    

        if isReroute: 
            for i, order in enumerate(self.customers.orders): 
                if order.status == 2 and order.type == 1:
                    routing.VehicleVar(manager.NodeToIndex(i+1)).SetValues([order.vehicle.vehicle_index])

            curr_solution = []
            print(self.routes_list)
            for route in list(self.routes_list.values()):
                temp = []
                print(route)
                if route!=-1:
                    for node in route.route:
                        if node.status in [3,4]:
                            continue
                        else:
                            temp.append(node.current_vrp_index)
                    curr_solution.append(temp)
            print(curr_solution)
            initial_solution = routing.ReadAssignmentFromRoutes(curr_solution,True)
            routing.CloseModelWithParameters(parameters)
            solution = routing.SolveFromAssignmentWithParameters( initial_solution, parameters)
        
        else:
            solution = routing.SolveWithParameters(parameters)

    
        

        if solution: 
            # Process Solution
            self.update_routed_order_status(manager, routing, solution)
            self.build_vehicle_routes(manager, routing, solution)
            return manager, routing, solution
            
    def bin_pack(self, vehicle_id, order_ids, dimensions):
        pass