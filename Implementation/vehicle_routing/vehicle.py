import matplotlib.pyplot as plt

class Vehicle:
    def __init__(self, total_volume_capacity, vehicle_status=None, current_location=0, alotted_packages=None, start=None, end=None, last_node=None, next_node=None, current_node=None, route=None,current_trip=None):
        #locations should be an object
        self.vehicle_status = vehicle_status
        self.total_volume_capacity = total_volume_capacity
        self.actual_volume_capacity = total_volume_capacity
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
        
        
    def update_container_volume(self, order_id, order_status, load_volume, order_type):
        self.route[self.route.find(order_id)]=order_status
        if order_type==0: #pickup
            pass
        else:
            pass
        if order_status==4: #successful
            self.total_volume_capacity -= load_volume
            self.available_volume_capacity -= load_volume
        else:
            pass
        if order_status==4: #successful
            self.available_volume_capacity += load_volume
        else:
            self.total_volume_capacity -= load_volume
            self.available_volume_capacity -= load_volume
        return

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

# vehicle_list is a list of vehicles objects so whenever a change is made in the vehicle object it is refected here
class Fleet:
    def __init__(self, vehicle_list):
        self.num_vehicles = len(vehicle_list)
        self.vehicle_list = self.process_vehicle_list(vehicle_list)
        # self.vehicle_ids = [vehicle.id for vehicle in vehicle_list]
        self.capacities = [vehicle.actual_volume_capacity for vehicle in vehicle_list]
        self.routes = [vehicle.route for vehicle in vehicle_list]
        self.current_locations = [vehicle.current_node for vehicle in vehicle_list]
        # self.starting_position = [vehicle.start for vehicle in vehicle_list]
    
    def process_vehicle_list(self, vehicle_list):
        for idx, vehicle in enumerate(vehicle_list):
            vehicle.vehicle_index = idx

        return vehicle_list
        
    def get_total_vol_cap(self):
        return sum([vehicle.total_volume_capacity for vehicle in self.vehicle_list])

    def update_vehicles(self):
        self.num_vehicles = len(self.vehicle_list)
        self.capacities = [vehicle.total_volume_capacity for vehicle in self.vehicle_list]
        self.routes = [vehicle.route for vehicle in self.vehicle_list]
        self.current_locations = [vehicle.current_node for vehicle in self.vehicle_list]
        # self.starting_position = [vehicle.start for vehicle in self.vehicle_list]

    def set_starts_ends(self):
        print(self.vehicle_list[0].start.current_vrp_index)
        self.starts = [v.start.current_vrp_index for v in self.vehicle_list]
        self.ends = [0] * len(self.starts)
        
            
      