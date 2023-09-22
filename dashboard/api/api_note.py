from pprint import pprint

import flask
import requests

from dashboard.api.api_client import construct_url
from dashboard.model.note import Note


def get_all_notes(auth_cookie = None):
    url = construct_url("notes")
    res = requests.get(
        url=url,
        headers={"Authorization": f"Bearer {auth_cookie}"} if auth_cookie is not None else {},
    )
    if 400 <= res.status_code < 500:
        # if cookie is too old, initial call will fail
        print(f"Get Notes:  status={res.status_code}, try again...")
        res = requests.get(url=url)
    print(f"Get Notes:  status={res.status_code}")
    if res.status_code == 200:
        return res.json()
    return []


def update_note(note: Note, auth_cookie):
    url = construct_url(f"note/{note.id}")
    res = requests.patch(
        url=url,
        json=dict(content=note.to_dict()),
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    print(f"Update Note: id={note.id}, status={res.status_code}")
    if res.status_code == 200:
        return True
    else:
        return False

def create_note(note: Note, auth_cookie):
    url = construct_url("notes")
    res = requests.post(
        url=url,
        json=note.to_dict(),
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    print(f"Create Note: id={note.id}, status={res.status_code}")
    return True


def delete_annotation(note_id, auth_cookie):
    url = construct_url(f"note/{note_id}")
    res = requests.delete(url=url, headers={"Authorization": f"Bearer {auth_cookie}"})
    print(f"Delete Note: id={note_id}, status={res.status_code}")
    return True
