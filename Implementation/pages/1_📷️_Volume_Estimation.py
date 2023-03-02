import streamlit as st

st.set_page_config(page_title="Volume Estimation", page_icon="📷️")

st.title("Stereoscopic Depth-Based Multi-Modal Volume Approximation")

st.header("Methodology")

# st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/setup1.png", width=400)
# st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/setup2.png", width=300)

st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/Frame 48096285.png", width=800)

st.subheader("The flow of the entire process")
st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/flow1.png")

st.subheader("How do we get volume from the shape?")
st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/flow2.png")

st.header("Key advantages")
st.markdown("""
    - Can be **scaled upwards** using a conveyor belt and the **same RealSense camera** can be used in an industrial setting.
    - **Handling moving objects** and **no manual intervention** in scanning.
    - **Realtime and efficient** because of using very light Deep Learning models and using shape-wise calculations.
    - More accurate than pure Deep Learning based methods.
    - Can compete against LiDAR based approaches **without using point cloud.**
""")

st.header("Results")
st.markdown("We have obtained significant improvement by using the current **stereoscopic depth method** instead of the RGB-to-pointcloud approach. For this, we use the Intel Realsense Camera.")
st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/table.png")