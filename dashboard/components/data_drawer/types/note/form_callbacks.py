from dash import Output, Input, State
from dash.exceptions import PreventUpdate

from dashboard.config.id import *
from dashboard.maindash import app


@app.callback(
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_EDIT_BUTTON, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def store_edited_note_id(edit_click, data):
    if edit_click is None or edit_click == 0:
        raise PreventUpdate
    return dict(id=data["note_id"])


@app.callback(
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def store_edited_note_id(save_click, _):
    if save_click is None or save_click == 0:
        raise PreventUpdate
    return dict(id=None)


@app.callback(
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def store_edited_note_id(cancel_click, _):
    if cancel_click is None or cancel_click == 0:
        raise PreventUpdate
    return dict(id=None)


@app.callback(
    Output(ID_NOTES_STORE, "data"),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State(ID_NOTES_STORE, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_NOTE_EDIT_TITLE, "value"),
    State(ID_NOTE_EDIT_DESCRIPTION, "value"),
    prevent_initial_call=True
)
def save_note_changes(click, notes, current_note, title, description):
    if click is None or click == 0:
        raise PreventUpdate

    note_id = current_note["note_id"]
    for note in notes:
        if note["note_id"] == note_id:
            note["title"] = title
            note["description"] = description

    current_note["title"] = title
    current_note["description"] = description
    return notes, current_note
