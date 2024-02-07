import dash
import dash_mantine_components as dmc
import flask
from dash import html, Output, Input, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from http.client import responses
from configuration import PRIMARY_COLOR
from src.api.api_note import delete_note
from src.config.id_config import *
from src.model.note import Note
from src.util.util import pretty_date
from src.main import app


def text_to_html_list(text: str):
    text_list = text.split("\n")
    children = []
    for para in text_list:
        children.append(para)
        children.append(html.Br())
    return children

def list_item(text, icon):
    return dmc.ListItem(
        text,
        icon=dmc.ThemeIcon(
            DashIconify(icon=icon, width=16),
            radius="xl",
            color=PRIMARY_COLOR,
            size=24,
        ),
    )


icon_private = DashIconify(icon="material-symbols:lock",                    width=14, color="#868e96", style={"display":"block", "marginLeft":"3px"})
icon_public  = DashIconify(icon="material-symbols:lock-open-right-outline", width=14, color="#868e96", style={"display":"block", "marginLeft":"3px"})

def note_detail_view(note: Note):
    return [
        dmc.Grid([
            dmc.Col(
                html.Span([
                    dmc.Text(
                        f"{note.author if note.author is not None else 'unknown'} | {pretty_date(note.date) if note.date is not None else '-'} |",
                        size="xs",
                        color="dimmed",
                        style={"display":"block"},
                    ),
                    dmc.Text(icon_public if note.public else icon_private),
                ],
                    style={"display":"inline-flex"}
                ),
                span="content"),
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(dmc.Divider(size="xs")),
            dmc.Col(
                dmc.Spoiler(
                    text_to_html_list(note.description),
                    showLabel="Show more",
                    hideLabel="Hide",
                    maxHeight=250,
                ),
                span=12
            ),
        ])
    ]


@app.callback(
    Output(ID_CONFIRM_DELETE_DIALOG, "displayed", allow_duplicate=True),
    Input(ID_NOTE_DELETE_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def map_click(click):
    if click == 0 or click is None:
        raise PreventUpdate
    return True


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "is_open", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "children", allow_duplicate=True),
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Input(ID_CONFIRM_DELETE_DIALOG, "submit_n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def deactivate_edit_mode(delete_click, note):
    if delete_click is None or delete_click == 0:
        raise PreventUpdate

    auth_cookie = flask.request.cookies.get("auth")
    response = delete_note(note["data"]["id"], auth_cookie)
    if response == 200:
        return dict(data=None, inEditMode=False), False, dash.no_update, dash.no_update, dict(entries=[], type="Note")
    else:
        notification = [
            dmc.Title("Something went wrong!", order=6),
            dmc.Text("Could not delete Note."),
            dmc.Text(f"Exited with Status Code: {response} | {responses[response]}", color="dimmed")
        ]
        return dash.no_update, dash.no_update, True, notification, dash.no_update

