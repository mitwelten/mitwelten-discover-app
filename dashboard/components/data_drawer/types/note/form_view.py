import dash_mantine_components as dmc
from dash import Output, Input
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
    Output(ID_NOTE_EDIT_LAT, "value"),
    Output(ID_NOTE_EDIT_LON, "value"),
    Input(ID_SELECTED_NOTE_STORE, "data"),
)
def update_content_from_store(selected_note):
    print("update lat lon text field")
    if selected_note is None or selected_note["movedTo"] is None:
        raise PreventUpdate
    return selected_note["movedTo"][0], selected_note["movedTo"][1]
