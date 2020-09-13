import datetime
import typing as tp
from copy import deepcopy
from io import BytesIO

import numpy as np
import pandas as pd
import requests
import streamlit as st
from PIL import Image

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
    try:
        params = dict(
            key=key,
            photoreference=obj['photos'][0]['photo_reference'],
            maxwidth=150
        )
    except KeyError:
        return None
    res = requests.get(
        "https://maps.googleapis.com/maps/api/place/photo", params=params)
    res = requests.get(res.url)
    return Image.open(BytesIO(res.content))


@st.cache
def near_by_types_cached(key: str, location: tp.Tuple[float], radius: int, types: tp.List[str], **kwargs):
    return maps.near_by_types(key, location, radius, types, **kwargs)


cfg = maps.get_config()

nazwy_zatloczenie = {
    -5: "Zbyt niskie do śledzenia",
    -2: "Bardzo niskie",
    -1: "Poniżej średniej",
    0: "Typowe",
    1: "Powyżej średniej",
    2: "Bardzo wysokie",
    5: "Brak danych"
}

image = Image.open('logo.png')
st.image(image, width=150)
st.title("Zabierz mnie")

wspol = (float(st.number_input("Podaj szerokość geograficzną: ", value=maps.get_location()[
         0])), st.number_input("Podaj wysokość geograficzną: ", value=maps.get_location()[1]))
category_group = cfg['places'][st.selectbox(
    "Gdzie chcesz uciec?", tuple(cfg['places'].keys()))]
radius = st.slider('Maksymalna odległość', min_value=1,
                   max_value=30, value=15, step=1, format="%d minut(y)")
min_stars = st.slider('Minimalna liczba gwiazdek', min_value=0.0,
                      max_value=5.0, value=2.5, step=0.5, format="%f gwiazdek")
max_cena = st.slider('Maksymalny zakres cenowy', min_value=0,
                     max_value=4, value=0, step=1, format="%d dolar")

metry = st.sidebar.number_input(
    'Odległość do wyszukiwania', value=2000, step=100)

st.header('Miejsca')
with st.spinner("Weź długi oddech, policz do trzech, następnie wypuść powietrze ponownie licząc do trzech..."):
    try:
        # Sortowanie i filtracja
        # Pobieranie info
        ans = deepcopy(maps.near_by_types(
            cfg['maps_api_key'], wspol, metry, category_group))
        # Sortowanie i selekcja
        maps.get_best(ans, radius, min_stars, max_cena)
        # Sortowanie według zatłoczenia
        if maps.is_possible_checktime(cfg['private_api_key']):
            today = datetime.date.today().strftime('%A')
            hour = datetime.datetime.now().hour
            maps.check_popularity(cfg['private_api_key'], ans, today, hour)
            maps.sorting_by(ans, 'popularity', 3)
        else:
            st.info("BRAKUJE CREDITÓW W API")
    except maps.NothingFoundError:
        st.text("Aplikacja niestety nie znalazła żadnego miejsca tego typu")
    else:
        # Wyświetlanie
        lat_long = {
            'lat': [i['geometry']['location']['lat'] for i in ans],
            'lon': [i['geometry']['location']['lng'] for i in ans]
        }
        st.map(data=pd.DataFrame.from_dict(lat_long), zoom=14)
        for i in ans:
            st.markdown("  \n ".join((f"### {i['name']}",
                                      f"**Dystans:** {i['time_text']}",
                                      f"**Adres:** {i['vicinity']}",
                                      f"**Zatłoczenie:** *{nazwy_zatloczenie[i.get('popularity', 5)]}*",
                                      f"**Zakres cenowy:** {get_price(i, '$')}  **Oceny:** {get_price(i, ':star:', type_='rating')}")))
            ph = get_photo(cfg['maps_api_key'], i)
            if not ph is None:
                st.image(ph, width=150)
