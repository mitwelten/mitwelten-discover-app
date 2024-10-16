import requests

from src.api.api_client import construct_url
from src.model.note import Note


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

    print("Fetch notes failed: : Status Code ", res.status_code)
    return []


def update_note(note: Note, auth_cookie):
    url = construct_url(f"note/{note.id}")
    note_dict = note.to_dict()
    note_dict["note_id"] = note_dict["id"]
    res = requests.patch(
        url=url,
        json=note_dict,
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    print(f"Update Note: id={note_dict['id']}, status={res.status_code}")
    return res

def get_note_by_id(id: str, auth_cookie):
    url = construct_url(f"note/{id}")
    res = requests.get(
        url=url,
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    print(f"Get Note by id: id={id}, status={res.status_code}")
    return res


def create_note(note: Note, auth_cookie):
    url = construct_url("notes")
    res = requests.post(
        url=url,
        json=note.to_dict(),
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    print(f"Create Note: id={note.id}, status={res.status_code}")
    return res


def delete_note(note_id, auth_cookie):
    url = construct_url(f"note/{note_id}")
    res = requests.delete(url=url, headers={"Authorization": f"Bearer {auth_cookie}"})
    print(f"Delete Note: id={note_id}, status={res.status_code}")
    return res


def add_tag_by_note_id(note_id, tag:str, auth_cookie):
    url = construct_url(f"note/{note_id}/tag")
    response = requests.post(
        url=url,
        json=dict(name=tag),
        headers={"Authorization": f"Bearer {auth_cookie}"}
    )
    return response.status_code


def add_file_to_note(note_id, object_name, name, content_type, auth_cookie):
    url = construct_url(f"note/{note_id}/file")
    payload = dict(type=content_type, name=name, object_name=object_name)
    res = requests.post(
        url=url,
        json=payload,
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    return res


def delete_tag_by_note_id(note_id, tag:str, auth_cookie):
    url = construct_url(f"note/{note_id}/tag")
    res = requests.delete(
        url=url,
        json=dict(name=tag),
        headers={"Authorization": f"Bearer {auth_cookie}"}
    )
    print(f"Delete Tag of Note: id={note_id}, tag={tag}, status={res.status_code}")
    return res.status_code
