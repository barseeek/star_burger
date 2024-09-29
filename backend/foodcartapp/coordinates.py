import requests
from requests import HTTPError

from django.conf import settings


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_place_coordinates_by_address(apikey, address):
    try:
        restaurant_coordinates = fetch_coordinates(settings.YANDEX_API_KEY, address)
    except (HTTPError, ConnectionError):
        restaurant_coordinates = None
    lat, lon = restaurant_coordinates if restaurant_coordinates else (None, None)
    return lat, lon
