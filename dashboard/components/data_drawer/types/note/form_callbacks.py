import random

import dash
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
def activate_edit_mode(edit_click, selected_note):
    if edit_click is None or edit_click == 0:
        raise PreventUpdate
    return dict(data=selected_note["data"], inEditMode=True, isDirty=False)


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def map_click(click, selected_note):
    if click is None or click == 0:
        raise PreventUpdate

    if selected_note["data"] is None:
        return False, dash.no_update, dash.no_update

    if selected_note["isDirty"]:
        return dash.no_update, True, dash.no_update

    return False, dash.no_update, dict(data=None, inEditMode=False, isDirty=False)


@app.callback(
    Output({"role": "Notes", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State({"role": "Notes", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def save_note_changes(click, notes, selected_note):
    if selected_note is None or click is None or click == 0:
        raise PreventUpdate

    note_data = Note(selected_note["data"])
    found = False
    new_entries = []

    for note in notes["entries"]:
        if note["id"] == note_data.id:
            found = True
            new_entries.append(note_data.to_dict())
        else:
            new_entries.append(note)

    if not found:
        # new created note
        note_data.id = random.randint(0, 100000)  # TODO: connect to backend
        new_entries.append(note_data.to_dict())

    notes["entries"] = new_entries
    return notes, dict(data=note_data.to_dict(), inEditMode=False, isDirty=False)
