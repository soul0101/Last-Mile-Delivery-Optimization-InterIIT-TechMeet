import math
import numpy as np
import typing
from sklearn.metrics import pairwise

class Node:
    def __init__(self, coordinates, type, volume=0, status=0):
        """        
        Type: 
        ------
        0 : Depot
        1 : Delivery
        2 : Pickup
        
        Status: 
        --------
        0 : Unrouted 
        1 : Postponed
        2 : Scheduled
        3 : Success
        4 : Failed

        update_order_stattus : updating the status of the order about whether it is successful or failed.
        """
        self.lat = coordinates[0]
        self.lon = coordinates[1]
        self.coordinates = coordinates
        self.type = type 
        self.volume = volume
        self.current_vrp_index = None
        # self.next_vrp_index = None
        self.status = status
        
class Order(Node):
    """
      Extends class Node and stores other non-fixed quantities
    """
    def __init__(self, volume, coordinates, type, AWB=None, SKU=None, carryforward_penalty=1000000, status=0, vehicle=None, orientation=None, position=None):
        super().__init__(coordinates, type, volume, status)
        self.AWB = AWB
        self.SKU = SKU
        self.carryforward_penalty = carryforward_penalty
        self.vehicle = vehicle
        self.orientation = orientation
        self.position = position
        
    def update_order_status(self, new_status):
        if self.type == 1:
            if new_status == 4:
                # Delivery failed: Reduce vehicle capacity by order volume
                self.vehicle.actual_volume_capacity -= self.volume
                self.vehicle.available_volume_capacity -= self.volume
        if self.type == 2:
            if new_status == 3:
                # Pickup Successful: Reduce vehicle capacity by order volume
                self.vehicle.actual_volume_capacity -= self.volume
                self.vehicle.available_volume_capacity -= self.volume
        
        self.status = new_status

class Customers():
    """
      depot  : Location of Depot
      orders : list of orders scheduled to be delivered or are unrouted ( Not the ones that are failed or delivered or postponed)

      process_orders(orders) : generates a list of orders scheduled to be delivered or are unrouted

      process_customers() : generates a list of customers whose deliveries are scheduled today

      set_manager(manager) : set the manager for the VR Solver

      make_distance_mat(method) : generates the distance matrix based on the locations in the objects of Class Node. The default method is haversine here. ( Will be changed to OSRM)
        parameters:
            method : "haversine" (default), "euclidean", "osrm"
    
      get_total_volume() : Return the total demand of all customers.

      return_dist_callback(**kwargs) : Return a callback function for the distance matrix. kwargs arepassed to distance_mat

      return_delivery_callback() : returns a function  delivery_return(from_index) which returns the volume of delivery at that location

      make_service_time_call_callback() : Return a callback function that provides the time spent servicing the customer.

      make_transit_time_callback() : Creates a callback function for transit time. Assuming an average speed of speed_kmph

    """
    def __init__(self, depot, orders, service_time = 5):
        self.depot = depot
        self.number = None
        self.orders = self.process_orders(orders)
        self.customers = self.process_customers()
        self.service_time = service_time

    def process_orders(self, orders: list) -> list:
        order_list = []
        for order in orders:
            if order.status in [0, 2]:
                order_list.append(order)
        return order_list

    def process_customers(self) -> list:
        customer_list = [self.depot] + self.orders
        for idx, c in enumerate(customer_list):
            # Storing the new indexes of the orders in new list as class attribute. This wil be needed for solving VRP 
            c.current_vrp_index = idx
        
        self.number = len(customer_list)
        return customer_list
            
    def set_manager(self, manager):
        self.manager = manager

    def make_distance_mat(self, method='haversine'):
        """
        Return a distance matrix and make it a member of Customer, using the
        method given in the call. Currently only Haversine (GC distance) is
        implemented, but Manhattan, or using a maps API could be added here.
        Raises an AssertionError for all other methods.
        Args: method (Optional[str]): method of distance calculation to use. The
        Haversine formula is the only method implemented.
        Returns:
            Numpy array of node to node distances.
        Examples:
            >>> dist_mat = customers.make_distance_mat(method='haversine')
            >>> dist_mat = customers.make_distance_mat(method='manhattan')
            AssertionError
        """
        if method == 'haversine':
            self.distmat = self._haversine(self.customers)
        elif method == 'euclidean':
            self.distmat = self._euclidean(self.customers)
        else:
            #OSRM
            pass

    def _euclidean(self, nodes):
        # calculate the distance matrix using the euclidean method
        input_locations = [[math.radians(float(o.lat)), math.radians(float(o.lon))] for o in nodes]
        return np.ceil(pairwise.euclidean_distances(input_locations) * 1000)

    def _haversine(self, nodes):
        # calculate the distance matrix using the haversine method
        input_locations = [[math.radians(float(o.lat)), math.radians(float(o.lon))] for o in nodes]
        return np.ceil(pairwise.haversine_distances(input_locations) * 637100)

    def get_total_volume(self):
        """
        Return the total demand of all customers.
        """
        return (sum([c.volume for c in self.customers]))

    def return_dist_callback(self, **kwargs):
        """
        Return a callback function for the distance matrix.
        Args: **kwargs: Arbitrary keyword arguments passed on to
        make_distance_mat()
        Returns:
            function: dist_return(a,b) A function that takes the 'from' node
                index and the 'to' node index and returns the distance in km.
        """
        self.make_distance_mat(**kwargs)
        print(self.distmat)

        def dist_return(from_index, to_index):
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return int(self.distmat[from_node][to_node])

        return dist_return

    def return_delivery_callback(self):
        def delivery_return(from_index):
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = self.manager.IndexToNode(from_index)
            delivery_node = self.customers[from_node]
            if delivery_node.type == 1:
                return int(-delivery_node.volume)
            else:
                return 0

        return delivery_return
        
    def return_load_callback(self):
        def load_return(from_index):
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = self.manager.IndexToNode(from_index)
            delivery_node = self.customers[from_node]
            if delivery_node.type == 1:
                return int(-delivery_node.volume)
            elif delivery_node.type == 2:
                return int(delivery_node.volume)
            else:
                return 0

        return load_return

    def make_service_time_call_callback(self):
        """
        Return a callback function that provides the time spent servicing the
        customer. Default 300 seconds per unit demand.
        Returns:
            function [dem_return(a, b)]: A function that takes the from/a node
                index and the to/b node index and returns the service time at a
        """

        def service_time_return(a, b):
          return self.service_time

        return service_time_return

    def make_transit_time_callback(self, speed_kmph=25):
        """
        Creates a callback function for transit time. Assuming an average
        speed of speed_kmph
        Args:
            speed_kmph: the average speed in km/h
        Returns:
            function [transit_time_return(a, b)]: A function that takes the
                from/a node index and the to/b node index and returns the
                transit time from a to b.
        """

        def transit_time_return(a, b):
            return (self.distmat[a][b] / (speed_kmph * 1000 / 60))

        return transit_time_return