import os

import requests

def get_estimate(start_lat, start_lon, end_lat, end_lon, token):
    """
    Given two pairs of coordinates for a trip, return estimates
    from the Uber API.
    """
    endpoint = "https://api.uber.com/v1/estimates/price"
    params = {
        'start_latitude': start_lat,
        'start_longitude': start_lon,
        'end_latitude': end_lat,
        'end_longitude': end_lon,
        'server_token': token
    }
    r = requests.get(endpoint, params=params)
    r.raise_for_status()
    return r.json().pop('prices', [])