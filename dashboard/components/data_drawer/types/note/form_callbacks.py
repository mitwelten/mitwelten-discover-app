import random
from datetime import datetime
from pprint import pprint

import dash
from dash import Output, Input, State, ALL
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
    print("callback: edit button")
    if edit_click is None or edit_click == 0:
        print("no update")
        raise PreventUpdate
    return dict(data=selected_note["data"], inEditMode=True, movedTo=None)


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_NEW_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def store_edited_note_id(cancel_click, selected_note):
    print("callback: cancel button")
    if cancel_click is None or cancel_click == 0:
        print("no update")
        raise PreventUpdate
    return dict(data=selected_note["data"], inEditMode=False, movedTo=None), None


@app.callback(
    Output({"role": "Notes", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_NEW_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State({"role": "Notes", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_NOTE_EDIT_TITLE, "value"),
    State(ID_NOTE_EDIT_DESCRIPTION, "value"),
    prevent_initial_call=True
)
def save_note_changes(click, notes, selected_note, title, description):
    if selected_note is None:
        raise PreventUpdate
    print("callback: save button")
    if click is None or click == 0:
        print("no update")
        raise PreventUpdate

    note_data = Note(selected_note["data"])
    position = selected_note.get("movedTo", [note_data.lat, note_data.lon])

    note_data.title = title
    note_data.description = description
    note_data.lat = position[0]
    note_data.lon = position[1]
    note_data.updated_at = datetime.now().isoformat()

    found = False
    new_entries = []
    for note in notes["entries"]:
        if note["id"] == note_data.id:
            found = True
            new_entries.append(note_data.to_dict())
        else:
            new_entries.append(note)

    if not found:
        note_data.id = random.randint(0, 100000)
        new_entries.append(note_data.to_dict())
    notes["entries"] = new_entries
    return notes, dict(data=note_data.to_dict(), movedTo=None, inEditMode=False), None
