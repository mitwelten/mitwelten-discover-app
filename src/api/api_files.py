import requests
import base64

from src.api.api_client import construct_url


def get_file(object_name, auth_cookie):
    url = construct_url(f"files/discover/{object_name}")
    res = requests.get(url=url, headers={"Authorization": f"Bearer {auth_cookie}"})
    print(f"Get File from Note: object_name={object_name}, status={res.status_code}")
    return None


def get_image(object_name, auth_cookie):
    url = construct_url(f"files/discover/{object_name}")
    headers={"Authorization": f"Bearer {auth_cookie}"} if auth_cookie is not None else {}

    res = requests.get(url=url, headers=headers)

    encoded_image = base64.b64encode(res.content).decode()
    encoded_image = "{}{}".format("data:image/jpg;base64, ", encoded_image)

    print(f"Get File from Note: object_name={object_name}, status={res.status_code}")
    return encoded_image

def add_file_to_note(note_id, file, auth_cookie):
    url = construct_url(f"note/{note_id}/file")

def add_file(file, name: str, auth_cookie):
    url = construct_url(f"files/discover")
    payload = {"file" : (name, file)}
    res = requests.post(
        url=url,
        files=payload,
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    return res



