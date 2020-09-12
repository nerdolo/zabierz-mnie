import requests
import json
import typing as tp

with open('config.json') as file:
    API_KEY = json.load(file)['api_key']


def get_config():
    try:
        with open('config.json', 'r') as file:
            j = json.load(file)
    except FileNotFoundError as e:
        j = None
    return j

class NothingFoundError(Exception):
    pass

def get_location():
    return 52.409373, 16.924296

def get_near(key: str, location: tp.Tuple[float], radius: int, **kwargs):
    """ Znajduje najbliższe miejsca
    :param key: API KEY
    :type key: str
    :param location: (latitude, longitude)
    :type location: tp.Tuple[float]
    :param radius: In meters
    :type radius: int
    """
    # Zwraca zdictowaną odpowiedź
    res = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json',
                       dict(key=key, radius=radius, location=", ".join((str(i) for i in location)), **kwargs)).json()
    if not res['results']:
        raise NothingFoundError
    else:
        return res['results']