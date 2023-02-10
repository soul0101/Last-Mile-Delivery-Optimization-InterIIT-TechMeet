import streamlit as st

st.set_page_config(page_title="Route Formation", page_icon="🛵")

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

def get_vrp_instance(delivery_file, pickup_file) -> None:
    depot, orders, vehicles = helper.generate_problem_from_file(delivery_file, pickup_file)
    vrp_instance = VRP(depot, orders, vehicles)
    return vrp_instance

def run_vrp(vrp_instance, isReroute=False):
    manager, routing, solution = vrp_instance.process_VRP(edge_weight_type='haversine', isReroute=isReroute)
    plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
    print(plan_output)
    print('dropped nodes: ' + ', '.join(dropped))
    print("Total Distance: ", total_distance)
    # vrp_instance.vehicle_output_plot(block=False)
    fig = vrp_instance.vehicle_return_plot(city_graph=True)
    print("plot created")
    st.pyplot(fig)
   
def plot(vrp_instance):
    fig = vrp_instance.vehicle_return_plot(city_graph=True)
    print("plot created")
    st.pyplot(fig)

def plot_scatter(vrp_instance, dynamic=False):
    fig = vrp_instance.vehicle_return_scatter(city_graph=True, dynamic=dynamic)
    print("plot created")
    st.pyplot(fig)

def st_ui():
    st.title("Capacitated Vehicle Routing with Dynamic Pickups")
    delivery_file = st.sidebar.file_uploader("Upload the Excel File containing Delivery Addresses", type=['xlsx', 'csv'])
    pickup_file = st.sidebar.file_uploader("Upload the Excel file containing the Pickup Addresses", type=['xlsx', 'csv'])
    if delivery_file is None:
        delivery_file = './mock/dispatch_testing.xlsx'
    if pickup_file is None:
        pickup_file = './mock/pickups_testing.xlsx'

    load_button = st.sidebar.button("Load")

    st.sidebar.header("Generate Routes")
    route_button = st.sidebar.button("Route")

    st.sidebar.header("Skip Time")
    minutes_slider = st.sidebar.slider("Pick the amount of minutes to skip", 0, 60, 30, 5)
    if 'vrp_instance' not in st.session_state:
        vrp_instance = get_vrp_instance(delivery_file=delivery_file, pickup_file=pickup_file)
        st.session_state['vrp_instance'] = vrp_instance
    
    skip_time_button = st.sidebar.button("Skip Time")

    st.sidebar.header("Add Dynamic Pickups")
    dynamic_pickup_button = st.sidebar.button("Add Dynamic")

    st.sidebar.header("Reroute Routes")
    reroute_button = st.sidebar.button("Reroute")

    if load_button:
        st.session_state['vrp_instance'] = get_vrp_instance(delivery_file=delivery_file, pickup_file=pickup_file)
        plot_scatter(st.session_state['vrp_instance'])

    if route_button:
        run_vrp(st.session_state['vrp_instance'])

    if skip_time_button:
        st.session_state['vrp_instance'].routes_list.skip_time(minutes_slider)
        plot(st.session_state['vrp_instance'])
    
    if dynamic_pickup_button:
        for i in range(5):
            st.session_state['vrp_instance'].add_dynamic_order(helper.generate_random_order(type=2))
        plot(st.session_state['vrp_instance'])

    if reroute_button:
        run_vrp(st.session_state['vrp_instance'], isReroute=True)


if __name__ == '__main__':
    st_ui()
