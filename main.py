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

config = maps.get_config()

st.sidebar.title("Konfiguracja")

st.sidebar.checkbox("")