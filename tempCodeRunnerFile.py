    # routes_list = vrp_instance.get_routes()
    # for vehicle_idx, route in routes_list.items():
    #     if route == -1:
    #         continue
    #     for i in range(3):
    #         route.next_node(3)

    # for i in range(5):
    #     vrp_instance.add_dynamic_order(helper.generate_random_order())
    
    # vrp_instance.city_graph.city.plot(facecolor="lightgrey", edgecolor="grey", linewidth=0.3)
    
    # manager, routing, solution = vrp_instance.process_VRP(isReroute=True)
    # vrp_instance.vehicle_output_plot()
    # plan_output, dropped, total_distance = helper.vehicle_output_string(manager, routing, solution)
    # print(plan_output)
    # print('dropped nodes: ' + ', '.join(dropped))
    # print('Total Distance: ', total_distance)