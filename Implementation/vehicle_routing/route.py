from vehicle_routing.customers import Order, Node

class Route:
    def __init__(self, route, vehicle):
        self.route = route
        self.current_node = 0
        self.vehicle = vehicle

    def next_node(self, new_status):
        """
        Status:
        3 : Success
        4 : Fail
        """

        if self.current_node != 0:
            self.route[self.current_node].update_order_status(new_status)
            print("status", self.route[self.current_node].status)

        if self.current_node < len(self.route):
            self.current_node += 1
            self.vehicle.start = self.route[self.current_node]

    def get_current_node(self):
        return self.route[self.current_node]