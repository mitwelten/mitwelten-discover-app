import dash
import dash_mantine_components as dmc
from dash import Output, Input, ALL, State, html
from dash.exceptions import PreventUpdate
from dash_cool_components import TagInput

from configuration import PRIMARY_COLOR
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note


def note_form(note: Note):
    return [
        dmc.Grid([
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(html.Div(TagInput(value=[{"index":0, "displayValue":"helo"}])), span=12),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_TITLE, value=note.title, label="Title", variant="filled"), span=12),
            dmc.Col(dmc.Textarea(id=ID_NOTE_EDIT_DESCRIPTION, value=note.description, label="Description", variant="filled"), span=12),
            dmc.Divider(size="sm"),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_LAT, label="Latitude", value=note.lat, variant="filled"), span="content"),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_LON, label="Longitude", value=note.lon, variant="filled"), span="content"),
        ]),
        dmc.Grid([
            dmc.Col([dmc.Button("Cancel", id=ID_NOTE_FORM_CANCEL_BUTTON, type="reset", color="gray")], span="content"),
            dmc.Col(dmc.Button("Save", id=ID_NOTE_FORM_SAVE_BUTTON, type="submit"), span="content"),
        ],
            justify="flex-end"
        )
    ]


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_EDIT_TITLE, "value"),
    Input(ID_NOTE_EDIT_DESCRIPTION, "value"),
    Input(ID_NOTE_EDIT_LAT, "value"),
    Input(ID_NOTE_EDIT_LON, "value"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    prevent_initial_call=True
)
def update_note_store_by_form(title, description, lat, lon, selected_note, all_notes):
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

    selected_note["data"]["title"] = title
    selected_note["data"]["description"] = description
    selected_note["data"]["location"]["lat"] = float(lat)
    selected_note["data"]["location"]["lon"] = float(lon)

    # if selected note is not modified(dirty), check if note is modified after callback has fired
    is_dirty = True
    found = False
    for note in all_notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            found = True
            is_dirty = Note(note) != Note(selected_note["data"])

    if not found:  # note is new created - therefore not in collection
        if title == "" and description == "":
            is_dirty = False  # callback was fired when mounting to de DOM

    is_edited = selected_note.get("inEditMode", False)
    return dict(data=selected_note["data"], inEditMode=is_edited, isDirty=is_dirty)


@app.callback(
    Output(ID_NOTE_EDIT_LAT, "value", allow_duplicate=True),
    Output(ID_NOTE_EDIT_LON, "value", allow_duplicate=True),
    Input({"role": "Note", "id": ALL, "label": "Node"}, "position"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def change_lat_lon_by_marker_position(_, selected_note):
    """Update value of lat & lon text fields when marker is moved and its position change"""
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

    new_position = None
    for pos in dash.ctx.inputs_list[0]:
        if selected_note["data"]["id"] == pos["id"]["id"]:
            new_position = pos["value"]

    return new_position

