import requests

from src.api.api_client import construct_url

def get_environment_data():
    url = construct_url(f"environment/entries")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    
    print("Fetch environment data failed: : Status Code ", response.status_code)
    return None


def get_environment_data_by_id(environment_id):
    url = construct_url(f"environment/entries/{environment_id}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    print("Fetch environment data by id failed: : Status Code ", response.status_code)
    return None


def get_environment_legend():
    url = construct_url(f"environment/legend")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    print("Fetch environment legend by id failed: : Status Code ", response.status_code)
    return []
