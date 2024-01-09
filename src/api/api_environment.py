import requests

from src.api.api_client import construct_url

def get_environment_data():
    url = construct_url(f"environment/entries")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_environment_data_by_id(environment_id):
    url = construct_url(f"environment/entries/{environment_id}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_environment_legend():
    url = construct_url(f"environment/legend")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None
