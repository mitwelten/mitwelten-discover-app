import requests

from dashboard.api.api_client import construct_url


def get_all_notes():
    url = construct_url("notes")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None
