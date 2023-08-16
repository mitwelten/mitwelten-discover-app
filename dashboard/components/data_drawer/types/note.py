import dash
import dash_mantine_components as dmc
from dash import Output, Input, ALL, State

from dashboard.api.api_client import get_fake_note_by_id
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note


def create_note_form(trigger_id, theme):
    note = get_fake_note_by_id(trigger_id)
    note = Note(note)


def create_form(note):
    return dmc.Text(f"Form of: {note}")


@app.callback(
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Input({"role": "Note", "label": "Store"}, "data"),
    prevent_initial_call=True
)
def create_note_form(data):
    print("draw note")
    return create_form(data)


@app.callback(
    Output({"role": "Note", "label": "Store"}, "data"),
    Output(ID_FOCUS_ON_MAP_LOCATION, "data", allow_duplicate=True),
    Input({"role": "Note", "id": ALL, "label": "Node"}, "n_clicks"),
    State(ID_NOTES_STORE, "data"),
    prevent_initial_call=True
)
def handle_note_click(_, data):
    print("note click")
    if dash.ctx.triggered_id is not None:
        for note in data:
            if note["note_id"] == dash.ctx.triggered_id["id"]:
                return note, note["location"]

    return dash.no_update
