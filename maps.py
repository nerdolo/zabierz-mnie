import requests
import json
import typing as tp

walking_time=20
minimum_rating=3.0

def write_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file)

def write_result(result):
    with open('result.json', 'w') as file:
        json.dump(result, file)


def get_config():
    try:
        with open('config.json', 'r') as file:
            j = json.load(file)
    except FileNotFoundError as e:
        j = None
    return j


class NothingFoundError(Exception):
    pass


def get_location() -> tp.Tuple[float]:
    return 52.409373, 16.924296


def get_near(key: str, location: tp.Tuple[float], radius: int, **kwargs) -> list:
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
    if not res.get('results', None):
        raise NothingFoundError
    else:
        return res['results']


def get_distance(key: str, start: tp.Tuple[float], dest: tp.Tuple[dict], **kwargs) -> None:
    destinations = "|".join((",".join(
        (str(i['geometry']['location']['lat']), str(i['geometry']['location']['lng']))) for i in dest))
    res = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json',
                       dict(key=key, departure_time='now', origins=f"{start[0]},{start[1]}", destinations=destinations, mode='walking', **kwargs)).json()
    try:
        dists = res['rows'][0]['elements']
    except (IndexError, KeyError):
        print(res.get('error_message', "No error message"))
        raise NothingFoundError
    else:
        for i, dist in enumerate(dists):
            dest[i]['time_text'] = dist['duration']['text']
            dest[i]['time_sec'] = dist['duration']['value']

def is_possible_checktime(key: str, _min = 3) -> bool:
    res = requests.get(f'https://besttime.app/api/v1/keys/{key}').json()
    return res['credits_forecast']>_min and res['credits_query']>_min

def check_time():
    pass

def result_sorting(results, walk_time, min_rate):
    i=0
    while i < len(results):
        try:
            if results[i]['business_status'] != 'OPERATIONAL':
                results.pop(i)
                continue
        except: print("Couldn't find business status for", i+1)

        try:
            if results[i]['opening_hours']['open_now'] == False:
                results.pop(i)
                continue
        except: print("Couldn't find opening hours", i+1)

        try:
            if results[i]['rating'] < min_rate:
                results.pop(i)
                continue
        except: print("Couldn't find rating", i+1)

        if results[i]['time_sec']/60 > walk_time:
            results.pop(i)
            continue
        i+=1



a = get_near(get_config()['maps_api_key'], get_location(), 2000)
get_distance(get_config()['maps_api_key'], get_location(), a)
write_result(a)
result_sorting(a,walking_time,minimum_rating)
print(a)

for i in a:
    print(i['name'], i['time_text'], int(i['time_sec']/60))
