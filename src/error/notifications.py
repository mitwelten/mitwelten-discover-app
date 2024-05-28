import dash_mantine_components as dmc
from http.client import responses


def notification(text: str):

    notification = [
        dmc.Title("Something went wrong!", order=6),
        dmc.Text(text),
    ]
    return notification


def notification_not_permitted(text: str):

    notification = [
        dmc.Title("Operation not permitted.", order=6),
        dmc.Text(text),
    ]
    return notification


def notification_response(code: int, text: str):

    code_desc = responses[code]

    notification = [
        dmc.Title("Something went wrong!", order=6),
        dmc.Text(text),
        dmc.Text(f"Status Code: {code} | {code_desc}", color="dimmed")]

    return notification
