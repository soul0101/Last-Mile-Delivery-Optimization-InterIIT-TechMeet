import streamlit as st
import os
import math
import random 
import numpy as np
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import shapefile as shp

from vehicle_routing.vrp import VRP 
import vehicle_routing.helper as helper

class VRPDeploy():
    def __init__(self, delivery_file, pickup_file) -> None:
        depot, orders, vehicles = helper.generate_problem_from_file(delivery_file, pickup_file)
        self.vrp_instance = VRP(depot, orders, vehicles)

    def runvrp(self):
        # Check time window solution
        # new_order = helper.generate_random_order(type=1, start_time=14, end_time=25)
        # vrp_instance.add_dynamic_order(new_order)

        manager, routing, solution = self.vrp_instance.process_VRP(edge_weight_type='osrm')
        # manager, routing, solution = vrp_instance.process_VRP(edge_weight_type='haversine')

        plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
        print(plan_output)
        print('dropped nodes: ' + ', '.join(dropped))
        print("Total Distance: ", total_distance)
        self.vrp_instance.export_shapefile()
        # vrp_instance.vehicle_output_plot(block=False)
        fig = self.vrp_instance.vehicle_return_plot_routes(city_graph=True)
        print("plot created")
        st.pyplot(fig)

    def skip(self, minutes_to_skip=0):
        self.vrp_instance.routes_list.skip_time(minutes_to_skip)
        manager, routing, solution = self.vrp_instance.process_VRP(isReroute=True)
        fig = self.vrp_instance.vehicle_return_plot()
        # self.vrp_instance.vehicle_return_plot()
        st.pyplot(fig)
        plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
        print(plan_output)
        print('dropped nodes: ' + ', '.join(dropped))
        print('Total Distance: ', total_distance)


with st.sidebar:
    delivery_file = st.file_uploader("Upload the Excel File containing Delivery Addresses", type=['xlsx', 'csv'])
    pickup_file = st.file_uploader("Upload the Excel file containing the Pickup Addresses", type=['xlsx', 'csv'])
    submit = st.button("Submit")

if submit:
    vrp_instance = VRPDeploy(delivery_file=delivery_file, pickup_file=pickup_file)
    vrp_instance.runvrp()
    minutes_slider = st.sidebar.slider("Pick the amount of minutes to skip", 0, 60, 0, 5)
    vrp_instance.skip(minutes_to_skip=minutes_slider)

