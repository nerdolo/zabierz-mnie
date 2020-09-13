import requests
import json
import typing as tp

def write_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file)

def get_config():
    try:
        with open('config.json', 'r') as file:
            j = json.load(file)
    except FileNotFoundError as e:
        j = None
    return j

def write_result(result):
    with open('result.json', 'w') as file:
        json.dump(result, file)

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
        return []
    else:
        return res['results']


def check_distance(key: str, start: tp.Tuple[float], dest: tp.Tuple[dict], **kwargs) -> None:
    """ Modyfikuje tablicę dest dodając do wartości w niej informacje o dystancie w sekundach i dystansie w formie tekstowej

    :param key: API_KEY
    :type key: str
    :param start: Położenie początkowe
    :type start: tp.Tuple[float]
    :param dest: Miejsca do zbadania; tablica jest modyfikowana
    :type dest: tp.Tuple[dict]
    :raises NothingFoundError: Nie znaleziono miejsc
    """
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


def near_by_types(key: str, location: tp.Tuple[float], radius: int, types: tp.List[str], **kwargs) -> tp.List[dict]:
    """Zwraca miejsca wymienionych typu w okolicy

    :param key: API KEY Google Maps
    :type key: str
    :param location: Współrzędne geograficzne (latitude, longitude)
    :type location: tp.Tuple[float]
    :param radius: Odległość w metrach
    :type radius: int
    :param types: Typy miejsc według Google
    :type types: tp.List[str]
    :return: Lokalizacje
    :rtype: tp.List[dict]
    """
    all_places = list()
    for i in types:
        new = get_near(key, location, radius, type=i)
        check_distance(key, location, new)
        all_places.extend(new)
    return all_places


def is_possible_checktime(key: str, _min = 3) -> bool:
    '''Sprawdza czy mamy creditsy na robienie testu; wymaga API_private_key'''
    res = requests.get(f'https://besttime.app/api/v1/keys/{key}').json()
    print(res['credits_forecast'], res['credits_query'])
    return res['credits_forecast']>_min and res['credits_query']>_min

def check_popularity(private_key: str, dests: tp.Tuple[dict], day: str, hour: int) -> None:
    """Modyfikuje tablicę dests dodając informacje o popularności dla określonej godziny i dnia tygodnia

    :param private_key: API key
    :type private_key: str
    :param dests: 
    :type dests: tp.Tuple[dict]
    :param day: Angielskie nazwy dni tygodnia, z dużej litery
    :type day: str
    :param hour: wartość godziny
    :type hour: int
    """
    for i in range(len(dests)):
        dests[i]['popularity'] = find(private_key, dests[i]['name'], dests[i]['vicinity'])[day][str(hour)]

def find(private_key: str, name: str, address: str) -> tp.Dict[str,int]:
    """Pobiera z dysku/serwera informacje na temat popularności miejsca 

    :param private_key: API key
    :type private_key: str
    :param name: Nazwa miejscówy
    :type name: str
    :param address: Adres miejsców
    :type address: str
    :return: Dictionary z popularnością dla godzin i dni tygodnia
    :rtype: tp.Dict[str,int]
    """
    with open('time_cache.json', 'r') as file:
        j = json.load(file)
    if f"{name}|||{address}" in j.keys():
        data = j[f"{name}|||{address}"]
    else:
        params = {
            'api_key_private':private_key,
            'venue_name':name,
            'venue_address':address
        }
        r = requests.request("POST", 'https://besttime.app/api/v1/forecasts', params=params)
        res = r.json()
        try:
            days = [(i["day_info"]['day_text'], i['hour_analysis']) for i in res['analysis']]
            write_result(days)
        except KeyError:
            data = -1
        else:
            data = dict()
            for day in days:
                data[day[0]] = dict()
                for i in day[1]:
                    data[day[0]][i['hour']] = i['intensity_nr']
        j[f"{name}|||{address}"] = data
    with open('time_cache.json', 'w') as file:
        json.dump(j, file)
    return data

def filter_(results: tp.List[dict], walk_time: int, min_rate: int):
    """Filtr

    :param results: Wyniki wyszukiwania miejsc
    :type results: tp.List[dict]
    :param walk_time: Dopuszczalny czas marszu w minutach
    :type walk_time: int
    :param min_rate: Minimalna ocena
    :type min_rate: int
    """
    i=0
    while i < len(results):
        try:
            if results[i]['business_status'] != 'OPERATIONAL':
                results.pop(i)
                continue
        except KeyError: print("Couldn't find business status for", i+1)

        try:
            if results[i]['opening_hours']['open_now'] == False:
                results.pop(i)
                continue
        except KeyError: print("Couldn't find opening hours", i+1)

        try:
            if results[i]['rating'] < min_rate:
                results.pop(i)
                continue
        except KeyError: print("Couldn't find rating", i+1)

        if results[i]['time_sec']/60 > walk_time:
            results.pop(i)
            continue
        i+=1


def sorting_(results: tp.List[dict]):
    results.sort(key= lambda x: x['time_sec'])

if __name__ == "__main__":
    if is_possible_checktime(get_config()['private_api_key']):
        print(find(get_config()['private_api_key'], 'Ogród Saski', 'Marszałkowska, 00-102 Warszawa'))
        is_possible_checktime(get_config()['private_api_key'])


#test
ans = near_by_types(get_config()['maps_api_key'], get_location(), 2000, get_config()['places']["2"])
filter_(ans,20,3.0)
sorting_(ans)
for a in ans:
    print(a['name'], int(a['time_sec']/60))