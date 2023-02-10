import streamlit as st

st.set_page_config(page_title="Flexibility", page_icon="📈")

st.title("Flexibility")

st.header("Balance Vehicle Utilization")
st.markdown("""
Economically, it makes sense to minimize the number of vehicles used, but there are cases where timely delivery of the orders has to be prioritized in which case our solution has the ability to **balance the vehicle loads among all the available vehicles** to minimize the time of delivery.

A two-step approach was employed to achieve this:
1. **Minimize** the max number of orders carried out by a vehicle.
2. **Penalize the solver** if the number of orders for a vehicle exceeds.
""")

st.image('/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/output_plot_1.png')
st.caption("Fig 1: Only one driver for the entire route")
st.image('/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/output_plot_2.png')
st.caption("Fig 2: Route divided for two drivers")

st.header("Incorporate Weather Conditions")
st.markdown("""The idea is to **incorporate the hyper-local area effects** on the routing distances, so that VRP model considers the data when optimizing the routes. 
One way to do this is to **increase the distance matrix cost** for points that lie in areas with bad weather conditions.
Weather-influenced VRP can ensure the routes are optimized for both distance and safety.
""")
st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/weather.png")
st.caption("A map of rainfall data of Bangalore")
# add chloropleth

# Just mention these things and refer them in one-pager
st.header("Time Windows")

st.header("Service Time")

st.header("Maximum Route Distance and Travel Time")