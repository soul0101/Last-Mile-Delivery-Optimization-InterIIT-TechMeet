import os
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Penalty Modelling", page_icon="⛔")

import base64
from pathlib import Path

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded
    
def img_to_html(img_path):
    img_html = "<img width=400 src='data:image/png;base64,{}' class='img-fluid'>".format(
      img_to_bytes(img_path)
    )
    return img_html

def st_ui():
    penalty_order = Image.open(os.path.join(os.path.dirname(__file__), 'assets/penalty_order.png'))

    st.header("Penalty Modelling")
    st.markdown("""
    We consider the EDD of the orders as well as the Order Density Centrality while calculating the order priority. 
    """)
    st.subheader("EDD Penalty")
    st.markdown("<p style='text-align: center; color: grey;'>"+img_to_html(os.path.join(os.path.dirname(__file__), 'assets/penalty_edd.png'))+"</p>", unsafe_allow_html=True)
    st.latex(r'''
    P_{EDD} = 1000 * e ^ {- \frac{\text{- Due in(days)}}{2}}
    ''')
    st.subheader("Order Centrality Penalty")
    st.markdown("""
    An order in nearby areas with a high order density has a high priority value, as drivers delivering in
    nearby areas can piggyback this order, saving fuel and time and reducing trips. To include this factor, the
    city is divided into tiles based on Bangalore's ward data. 

    But, there might be cases where an order lies in a ward with a low order density but the neighbouring
    tiles have a very high order density. To overcome this problem each tile's priority is calculated by taking
    into consideration the priority of its neighbours' as well.
    """)
    
    # st.image(penalty_order)
    st.image("/home/gunjan/Desktop/GrowSimplee/InterIIT-Optimization/Implementation/pages/assets/penalty_order.png")
    st.latex(r'''
    P_{\text{order density}} = e ^ {7 * \text{Order Density Centrality}}
    ''')

if __name__ == '__main__':
    st_ui()

