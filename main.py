import typing as tp
from copy import deepcopy

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
min_stars = st.slider('Minimalna liczba gwiazdek', min_value=0.0,
                   max_value=5.0, value=2.5, step=0.5, format="%d gwiazdek")

metry = st.sidebar.number_input(
    'Odległość do wyszukiwania', value=2000, step=100)


@st.cache
def near_by_types_cached(key: str, location: tp.Tuple[float], radius: int, types: tp.List[str], **kwargs):
    return maps.near_by_types(key, location, radius, types, **kwargs)

st.title('Miejsca')
with st.spinner("Weź długi oddech, policz do trzech, następnie wypuść powietrze ponownie licząc do trzech..."):
    ans = deepcopy(near_by_types_cached(cfg['maps_api_key'], wspol, metry, category_group))
    maps.filter_(ans, radius, min_stars) 
    maps.sorting_by(ans,'time_sec')

    lat_long = {
        'lat':[i['geometry']['location']['lat'] for i in ans],
        'lon':[i['geometry']['location']['lng'] for i in ans]
    }
    st.map(data=pd.DataFrame.from_dict(lat_long), zoom=14)
    st.write(ans[10])