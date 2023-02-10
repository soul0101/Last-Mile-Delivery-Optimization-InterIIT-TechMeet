import streamlit as st

st.set_page_config(page_title="Scalability", page_icon="📷️")

st.title("Scalability")

video_file2 = open('/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/streamlit/pages/assets/sweep2.mov', 'rb')
video_bytes2 = video_file2.read()

video_file = open('/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/streamlit/pages/assets/sweep1.mov', 'rb')
video_bytes = video_file.read()

st.video(video_bytes)



st.video(video_bytes2)