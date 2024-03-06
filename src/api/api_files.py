import requests
import base64
from pprint import pprint

from src.api.api_client import construct_url


def get_file(object_name, media_type, auth_cookie):
    url = construct_url(f"files/{object_name}")
    headers={"Authorization": f"Bearer {auth_cookie}"} if auth_cookie is not None else {}

    res = requests.get(url=url, headers=headers)

    encoded_file = base64.b64encode(res.content).decode()
    encoded_file = f"data:{media_type};base64,{encoded_file}"

    print(f"Get File from Note: object_name={object_name}, status={res.status_code}")
    return encoded_file


def add_file(file, name: str, content_type, auth_cookie):
    url = construct_url(f"files/discover")
    payload = {"file" : (name, file, content_type)}
    res = requests.post(
        url=url,
        files=payload,
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    return res


def delete_file(file_id, auth_cookie):
    url = construct_url(f"file/{file_id}")
    res = requests.delete(
        url=url,
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    return res

