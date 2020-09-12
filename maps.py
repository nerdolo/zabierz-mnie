import requests
import json
import typing as tp

with open('config.json') as file:
    API_KEY = json.load(file)['api_key']


def NothingFoundError(Exception):
    pass

def get_location():
    pass

def get_near(key: str, location: tp.Tuple[float], radius: int, types: tp.Tuple[str], **kwargs):
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
                       key=key, radius=radius, location=", ".join((str(i) for i in location), **kwargs)).json()
    if not res['results']:
        raise NothingFoundError
    else:
        return res['results']