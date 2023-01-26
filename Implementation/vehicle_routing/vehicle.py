import matplotlib.pyplot as plt

class Vehicle:
    """
        The class Vehicle stores the info about a spefic vehicle.
        total_volume_capacity : The total capacity of the cntainer with the delivery partner
        actual_volume_capacity : The current capacity of the container after accouting for items that are stuck there like failed deliveries and succful pickups.
        available_volume_capacity : the current available volume in the container
        current_location : The current location of the object (order object)
        last_node : The final node in this rute
        next_node : The next node in the route
        route : The route of this vehicle
        start : The starting node of the current route (this will store the current node before rerouting)
        end : The ending node of the current route
        vehicle_index : the current index of the vehicle in the vrp problem.

        Methods :
        
        set_route(route,start): Assign the route in "route" parameter to this vehicle. start indicated the starting node in the route.
       
        

    """
    def __init__(self, total_volume_capacity, vehicle_status=None, current_location=0, alotted_packages=None, start=None, end=None, last_node=None, next_node=None, current_node=None, route=None,current_trip=None):
        #locations should be an object
        #self.vehicle_status = vehicle_status
        self.total_volume_capacity = total_volume_capacity
        self.actual_volume_capacity = total_volume_capacity
        self.available_volume_capacity= total_volume_capacity
        self.current_location = current_location
        self.current_node = start
        self.last_node = last_node
        self.next_node = next_node
        self.route = route
        self.start = start
        self.end = end
        self.current_trip = current_trip
        self.vehicle_index = None

        if route != None:
            self.available_volume_capacity = total_volume_capacity - sum([order.volume for order in route])
        else:
            self.available_volume_capacity = total_volume_capacity

    
    def set_route(self,route,start):
        self.route = route
        self.last_node = None
        self.current_node = start
        self.start = start
        self.next_node = route[1]
        curr_vol_occ=0
        for order in self.route:
            curr_vol_occ += order.volume
        self.available_volume_capacity = self.total_volume_capacity - curr_vol_occ
        return
        
        
    # def update_container_volume(self, order_id, order_status, load_volume, order_type):
    #     self.route[self.route.find(order_id)]=order_status
    #     if order_type==0: #pickup
    #         pass
    #     else:
    #         pass
    #     if order_status==3: #successful
    #         self.total_volume_capacity -= load_volume
    #         self.available_volume_capacity -= load_volume
    #     else:
    #         pass
    #     if order_status==3: #successful
    #         self.available_volume_capacity += load_volume
    #     else:
    #         self.total_volume_capacity -= load_volume
    #         self.available_volume_capacity -= load_volume
    #     return

    def get_remaining_route(self,current_location):
        index = self.route.find(current_location)
        return self.route[index+1:]

    def update_location(self):
        self.last_node = self.current_node
        self.current_node = self.next_node
        nxt = self.route.index(self.route.next_node)
        self.next_node = self.route[self.route.index(self.route.next_node)+1]
        # The last node is always the depot so the edge case is taken care of

    def plot_container(self):
        pass
        # positions = [package["position"] for package in self.info_about_each_package]
        # x = [pos[0] for pos in positions]
        # y = [pos[1] for pos in positions]
        # plt.scatter(x, y)
        # plt.show()

class Fleet:
    """
        Fleet is a list of vehicles objects so whenever a change is made in the vehicle object it is refected here

        Attributes:
            num_vehicles : Number of vehicles available
            vehicle_list : List of indexes of vehicles (as according to the VRP solution)
            capacities : List of capacities of all vehicles ( list of object Vehicle)
            routes : List of routes (List of route objects)
            current_locations : list of current locations of all the vehicles.
            starts : List of starting locations of each vehicle
            ends : List of ending locations of each vehicle

        Methods:
            process_vehicle_list(vehicle_list) : sets the vehicle index attribute of the vehicle class according to the vehicle_list
            get_total_vol_cap : returns a list of the current volume capacities of the vehicles. ( Here actual volume capacity is returned)
            update_vehicles : Updates the information stored in the Fleet class
            set_starts_ends : sets the starting and ending indexes for each vehicle

    """
    def __init__(self, vehicle_list):
        self.num_vehicles = len(vehicle_list)
        self.vehicle_list = self.process_vehicle_list(vehicle_list)
        # self.vehicle_ids = [vehicle.id for vehicle in vehicle_list]
        self.capacities = [vehicle.actual_volume_capacity for vehicle in vehicle_list] #changed toal_vol to actual
        self.routes = [vehicle.route for vehicle in vehicle_list]
        self.current_locations = [vehicle.current_node for vehicle in vehicle_list]
        # self.starting_position = [vehicle.start for vehicle in vehicle_list]
    
    def process_vehicle_list(self, vehicle_list):
        for idx, vehicle in enumerate(vehicle_list):
            vehicle.vehicle_index = idx

        return vehicle_list
        
    def get_total_vol_cap(self):
        return sum([vehicle.actual_volume_capacity for vehicle in self.vehicle_list]) #changed total_vol to actual

    def update_vehicles(self):
        self.num_vehicles = len(self.vehicle_list)
        self.capacities = [vehicle.actual_volume_capacity for vehicle in self.vehicle_list] #changed total_vol to actual
        self.routes = [vehicle.route for vehicle in self.vehicle_list]
        self.current_locations = [vehicle.current_node for vehicle in self.vehicle_list]
        # self.starting_position = [vehicle.start for vehicle in self.vehicle_list]

    def set_starts_ends(self):
        print(self.vehicle_list[0].start.current_vrp_index)
        self.starts = [v.start.current_vrp_index for v in self.vehicle_list]
        self.ends = [0] * len(self.starts)
        
            
      