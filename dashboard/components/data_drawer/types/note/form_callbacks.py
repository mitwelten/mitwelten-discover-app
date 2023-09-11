from pprint import pprint

from dash import Output, Input, State
from dash.exceptions import PreventUpdate

from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_EDIT_BUTTON, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def store_edited_note_id(edit_click, selected_note):
    if edit_click is None or edit_click == 0:
        raise PreventUpdate
    return dict(data=selected_note["data"], inEditMode=True)


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def store_edited_note_id(cancel_click, selected_note):
    if cancel_click is None or cancel_click == 0:
        raise PreventUpdate
    return dict(data=selected_note["data"], inEditMode=False)


@app.callback(
    Output({"role": "Notes", "label": "Store", "type": "virtual"}, "data"),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State({"role": "Notes", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_NOTE_EDIT_TITLE, "value"),
    State(ID_NOTE_EDIT_DESCRIPTION, "value"),
    prevent_initial_call=True
)
def save_note_changes(click, notes, selected_note, title, description):
    if click is None or click == 0:
        raise PreventUpdate

    note_data = Note(selected_note["data"])

    for note in notes:
        if note["id"] == note_data.id:
            note["title"] = title
            note["description"] = description

    note_data.title = title
    note_data.description = description
    return notes, selected_note
