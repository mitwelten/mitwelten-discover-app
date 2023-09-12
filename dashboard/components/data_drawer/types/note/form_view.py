import dash
import dash_mantine_components as dmc
from dash import Output, Input, ALL, State
from dash.exceptions import PreventUpdate

from configuration import PRIMARY_COLOR
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note


def note_form(note: Note):
    print("render note_form")
    return [
        dmc.Grid([
            dmc.Col(dmc.Title(f"Note - {note.id}", order=5), span="content"),
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_TITLE, value=note.title ,label="Title", variant="filled"), span=12),
            dmc.Col(dmc.Textarea(id=ID_NOTE_EDIT_DESCRIPTION, value=note.description ,label="Description", variant="filled"), span=12),
            dmc.Divider(size="sm"),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_LAT, label="Latitude", value=note.lat, variant="filled"), span=6),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_LON, label="Longitude", value=note.lon, variant="filled"), span=6),
        ]),
        dmc.Grid([
            dmc.Col(dmc.Button("Cancel", id=ID_NOTE_FORM_CANCEL_BUTTON, type="reset", color="gray"), span="content"),
            dmc.Col(dmc.Button("Save", id=ID_NOTE_FORM_SAVE_BUTTON, type="submit"), span="content"),
        ],
            justify="flex-end"
        )
    ]


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data"),
    Input(ID_NOTE_EDIT_LAT, "value"),
    Input(ID_NOTE_EDIT_LON, "value"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def update_content_from_store(lat, lon, selected_note):
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

    is_edited = selected_note.get("inEditMode", False)
    return dict(data=selected_note["data"], movedTo=[float(lat), float(lon)], inEditMode=is_edited)


@app.callback(
    Output(ID_NOTE_EDIT_LAT, "value", allow_duplicate=True),
    Output(ID_NOTE_EDIT_LON, "value", allow_duplicate=True),
    Input({"role": "Notes", "id": ALL, "label": "Node"}, "position"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def update_marker_position(_, selected_note):
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

    new_position = None
    for pos in dash.ctx.inputs_list[0]:
        if selected_note["data"]["id"] == pos["id"]["id"]:
            new_position = pos["value"]

    return new_position

