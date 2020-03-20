import json
from typing import Dict

import requests


def request_directions(lat1: int, lng_1: int, lat2: int, lng_2: int, api_key: str) -> Dict:
    url = 'https://maps.googleapis.com/maps/api/directions/json?origin={origin_lat},{origin_lon}&destination={' \
          'dest_lat},{dest_lon}&key={api_key}' \
        .format(origin_lat=lat1, origin_lon=lng_1, dest_lat=lat2, dest_lon=lng_2, api_key=api_key)

    response = requests.get(url)
    if 'error_message' in json.loads(response.text):
        raise ValueError(json.loads(response.text)['status'], json.loads(response.text)['error_message'])

    return json.loads(response.text)
