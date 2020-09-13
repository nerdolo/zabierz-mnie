import typing as tp
from copy import deepcopy

import numpy as np
import pandas as pd
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

import maps


def get_price(place, char, type_='price_level'):
    val = place.get(type_, -1)
    if val == -1:
        return "*Brak danych*"
    elif val == 0:
        return "*Darmowe*"
    else:
        return char*int(val)

@st.cache
def get_photo(key, obj):
    params = dict(
        key=key,
        photoreference=obj['photos'][0]['photo_reference'],
        maxwidth = 150
    )
    res = requests.get("https://maps.googleapis.com/maps/api/place/photo", params=params)
    res = requests.get(res.url)
    return Image.open(BytesIO(res.content))


@st.cache
def near_by_types_cached(key: str, location: tp.Tuple[float], radius: int, types: tp.List[str], **kwargs):
    return maps.near_by_types(key, location, radius, types, **kwargs)


cfg = maps.get_config()

image = Image.open('logo.jpg')
st.image(image, width=600)
st.title("Zabierz mnie stąd")

wspol = (float(st.number_input("Podaj szerokość geograficzną: ", value=maps.get_location()[
         0])), st.number_input("Podaj wysokość geograficzną: ", value=maps.get_location()[1]))
category_group = cfg['places'][st.selectbox(
    "Gdzie chcesz uciec?", tuple(cfg['places'].keys()))]
radius = st.slider('Maksymalna odległość', min_value=1,
                   max_value=30, value=15, step=1, format="%d minut(y)")
min_stars = st.slider('Minimalna liczba gwiazdek', min_value=0.0,
                      max_value=5.0, value=2.5, step=0.5, format="%f gwiazdek")

metry = st.sidebar.number_input(
    'Odległość do wyszukiwania', value=2000, step=100)

st.header('Miejsca')
with st.spinner("Weź długi oddech, policz do trzech, następnie wypuść powietrze ponownie licząc do trzech..."):
    ans = deepcopy(near_by_types_cached(
        cfg['maps_api_key'], wspol, metry, category_group))
    maps.filter_(ans, radius, min_stars)
    # maps.sorting_by(ans, 'time_sec')

    lat_long = {
        'lat': [i['geometry']['location']['lat'] for i in ans],
        'lon': [i['geometry']['location']['lng'] for i in ans]
    }
    st.map(data=pd.DataFrame.from_dict(lat_long), zoom=14)
    for i in ans:
        st.markdown(f"### {i['name']} \n**Dystans:** {i['time_text']}  \n**Adres:** {i['vicinity']}  \n **Zakres cenowy:** {get_price(i, '$')}  **Oceny:** {get_price(i, ':star:', type_='rating')}")
        st.image(get_photo(cfg['maps_api_key'], i), width=150)