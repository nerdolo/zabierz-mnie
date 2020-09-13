import typing as tp

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

import maps

image = Image.open('logo.jpg')
st.image(image, width=600)
st.title("Zabierz mnie stąd")

cfg = maps.get_config()

wspol = (float(st.number_input("Podaj szerokość geograficzną: ", value=maps.get_location()[
         0])), st.number_input("Podaj wysokość geograficzną: ", value=maps.get_location()[1]))
category_group = cfg['places'][st.selectbox(
    "Gdzie chcesz uciec?", tuple(cfg['places'].keys()))]
radius = st.slider('Maksymalna odległość', min_value=1,
                   max_value=30, value=15, step=1, format="%d minut(y)")

metry = st.sidebar.number_input(
    'Odległość do wyszukiwania', value=2000, step=100)


@st.cache
def near_by_types_cached(key: str, location: tp.Tuple[float], radius: int, types: tp.List[str], **kwargs):
    return maps.near_by_types(key, location, radius, types, **kwargs)

st.title('Miejsca')
with st.spinner():
    near = near_by_types_cached(cfg['maps_api_key'], wspol, metry, category_group)

    lat_long = {
        'lat':[i['geometry']['location']['lat'] for i in near],
        'lon':[i['geometry']['location']['lng'] for i in near]
    }
    st.map(data=pd.DataFrame.from_dict(lat_long), zoom=14)
    st.write(near[10])