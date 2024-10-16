import requests
import base64
import logging

logger = logging.getLogger(__name__)

from src.api.api_client import construct_url


def get_file_url(object_name: str):
    return construct_url(f"files/{object_name}")

def get_file(object_name, media_type):
    url = construct_url(f"files/{object_name}")

    res = requests.get(url=url)

    encoded_file = base64.b64encode(res.content).decode()
    encoded_file = f"data:{media_type};base64,{encoded_file}"
    logger.info(f"Get File {object_name}: {res.status_code}")
    return encoded_file


def upload_file(file, name: str, content_type, auth_cookie):
    url = construct_url(f"files/discover")
    payload = {"file" : (name, file, content_type)}
    res = requests.post(
        url=url,
        files=payload,
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    logger.info(f"Upload File: {res.status_code}")
    return res


def delete_file(file_id, auth_cookie):
    url = construct_url(f"file/{file_id}")
    res = requests.delete(
        url=url,
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    logger.info(f"Delete File: {res.status_code}")
    return res

