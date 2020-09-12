import streamlit as st
import numpy as np
from PIL import Image
import maps

image = Image.open('logo.jpg')
st.image(image, width=600)
st.title("Zabierz mnie stąd")

wspol = (float(st.number_input("Podaj szerokość geograficzną: ")), st.number_input("Podaj wysokość geograficzną: "))
# st.map(data=, zoom=13)

is_outside = True if st.selectbox("Gdzie chcesz uciec?", ('Pod dach', 'Poza dach'))=="Poza dach" else False

# Sidebar
st.sidebar.title("Konfiguracja")
st.sidebar.title("Miejsca")
if not st.sidebar.checkbox("Zaznacz, aby się pokazało"):
    for i in config['places'].keys():
        config['places'][i] = st.sidebar.slider(i, min_value=0, max_value=2, value=config['places'][i])
    
