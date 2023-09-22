import random

import dash
import flask
from dash import Output, Input, State
from dash.exceptions import PreventUpdate

from dashboard.api.api_note import create_note
from dashboard.config.id_config import *
from dashboard.maindash import app
from dashboard.model.note import Note


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_EDIT_BUTTON, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def activate_edit_mode(edit_click, selected_note):
    """
    A click on the `Edit` button replaces the detail view by a form to edit note properties.
    :param edit_click: The edit button click-event of the note detail view.
    :param selected_note: The store containing the current selected note.
    :return: The modified selected note store. Property `inEditMode` is set to `True`.
    """
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
def map_click(cancel_click, selected_note):
    """
    Closing the drawer by click on the map.
    A modified note will not be stored, but a confirm dialog rises up.
    :param cancel_click: The cancel button click-event of the note form.
    :param selected_note: The store containing the current selected note.
    :return: The drawers state (open/closed) and optional a dialog to confirm unsaved changes.
    """
    if cancel_click is None or cancel_click == 0:
        raise PreventUpdate

    if selected_note["data"] is None:
        return False, dash.no_update, dash.no_update

    if selected_note["isDirty"]:
        return dash.no_update, True, dash.no_update

    return False, dash.no_update, dict(data=None, inEditMode=False, isDirty=False)


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_CHART_DRAWER, "opened"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def close_open_note_by_drawer_close_click(drawer_state, selected_note):
    """
    Handle the selected note when the drawer is closed by click on the close button.
    Click event is not available, therefore the callback listen on a state-change.
    """
    if drawer_state:
        raise PreventUpdate #  drawer state is opening - no action required

    if selected_note["data"] is None:
        raise PreventUpdate #  drawer contains not a note

    if selected_note["isDirty"]:
        return True, True, dash.no_update
    else:
        return dash.no_update, dash.no_update, dict(data=None, inEditMode=False, isDirty=False)


@app.callback(
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def add_note_to_store(click, notes, selected_note):
    """
    Insert an edited note into note store by clicking on the save button.
    The selected note will be cleared after a successful saving.
    """
    if selected_note is None or click is None or click == 0:
        raise PreventUpdate
    auth_cookie = flask.request.cookies.get("auth")
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
        note_data.public = True
        create_note(note_data, auth_cookie)
        # new_entries.append(new_note.to_dict())

    notes["entries"] = new_entries
    return notes, dict(data=note_data.to_dict(), inEditMode=False, isDirty=False)
