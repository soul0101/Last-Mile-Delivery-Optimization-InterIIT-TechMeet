import streamlit as st

st.set_page_config(page_title="Scalability", page_icon="⚖️")

st.title("Scalability")
st.markdown("""
CVRPMPD is an **NP-hard problem**, where SoTA solvers like OR tools struggle with large-scale datasets, around *5000 nodes*.
As the company scales up in cities, 5000+ orders will become common, which will *hamper scalability significantly*.
Clustering the nodes reduces the complexity by a large amount and allows CVRP solvers to **handle very large instances** with **low optimality gaps**.
""")

# st.header("Advantages of Clustering")
# st.markdown('''
# - **Reduced Complexity**: Dividing a large problem into smaller, more manageable sub-problems, making it easier to solve the VRP.
# - **Improved Scalability**: As the size of VRP increases, clustering handles the problem by dividing into smaller sub-problems.
# ''')

st.header("Sweep Algorithm")
st.markdown("""
- Used for grouping geographical coordinates based on their **cosine similarity** w.r.t. the depot.
- Sorts the orders according to **polar angles** and iteratively **sweeping a line in an angle** and grouping into clusters.
""")
st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/sweep.png")
st.caption("An illustration showing the Sweep Algorithm for Clustering")


st.header("Innovation")

st.markdown("""
Choosing the starting angle $θ_c= 0°$ is not efficient. 
In the below example where we start from 0°, we need to have **5 clusters** instead of the optimal **4 clusters**.
To allow for a small overall spread, we check the clustering for $θ_c$ in increments of 5°.

**Overall complexity:** $\mathcal{O}(n\log{}n)$
This way, we can evaluate how good the starting point is, by calculating the number of cluster and spread of points.
""")

st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/sweep2.png")
st.caption("Showing different starting points and associated clusters")

st.header("Benchmarks")
st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/benchmark.png")


st.subheader("Pseudocode for Sweep Clustering")

st.code('''
coords[Depo] = [0, 0]
θi(Polar Angle) of ith order = tan-1(lat(i) / long(i))
Sort customers according to θ in ascending order
Set cluster_id = 1
Set θc= 0°
Sweep customer by increasing θc, add customer to cluster.
Stop the sweep when we reach 500 nodes in the cluster.
cluster_id = cluster_id + 1
Repeat above 3 steps till we have completed allotment of all customers
''')