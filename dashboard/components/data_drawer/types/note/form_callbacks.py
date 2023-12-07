from datetime import datetime
from http.client import responses
from pprint import pprint

import dash
import flask
from dash import Output, Input, State
from dash.exceptions import PreventUpdate

import dash_mantine_components as dmc
from dashboard.api.api_note import create_note, update_note, delete_tag_by_note_id, add_tag_by_note_id
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


def find_new_tags(note_dict, all_tags):
    note_tags = note_dict["data"]["tags"]
    result_list = []
    for item in note_tags:
        if item not in all_tags:
            result_list.append(item["name"])

    return result_list

def find_deleted_tags(modified_note, original_note):
    result = []
    for t in original_note.tags:
        if t not in modified_note.tags:
            result.append(t)
    return result


def find_added_tags(modified_note, original_note):
    result = []
    for t in modified_note.tags:
        if t not in original_note.tags:
            result.append(t)
    return result


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "children", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "is_open", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_TAG_DATA_STORE, "data"),
    prevent_initial_call=True
)
def persist_note(click, notes, selected_note, all_tags):
    """
    Insert an edited note into note store by clicking on the save button.
    The selected note will be cleared after a successful saving.
    """
    if selected_note is None or click is None or click == 0:
        raise PreventUpdate
    auth_cookie = flask.request.cookies.get("auth")
    modified_note = Note(selected_note["data"])
    modified_note.date = datetime.now().isoformat()

    tags_to_delete = []
    tags_to_add    = []

    found = False
    response_code = 400
    returned_note_id = None

    for note in notes["entries"]:
        if note["id"] == modified_note.id:
            #  Note already exists
            found = True
            note = Note(note)
            tags_to_delete = find_deleted_tags(modified_note, note)
            tags_to_add = find_added_tags(modified_note, note)
            res = update_note(modified_note, auth_cookie)
            response_code = res.status_code
            returned_note_id = res.json().get("note_id", -1)

    if not found:
        # new created note
        res = create_note(modified_note, auth_cookie)
        response_code = res.status_code
        returned_note_id = res.json().get("note_id", -1)
        tags_to_add = modified_note.tags

    if response_code != 200 or returned_note_id == -1:
        notification = [
            dmc.Title("Something went wrong!", order=6),
            dmc.Text("Could not save Note."),
            dmc.Text(f"Exited with Status Code: {response_code} | {responses[response_code]}", color="dimmed")]
        return dash.no_update, dash.no_update, dash.no_update, True, notification

    # Persists deleted tag of a note
    if tags_to_delete:
        for t in tags_to_delete:
            delete_tag_by_note_id(returned_note_id, t, auth_cookie)
    # Persists added tags to a note
    if tags_to_add:
        for t in tags_to_add:
            add_tag_by_note_id(returned_note_id, t, auth_cookie)


    notes["entries"] = []
    return False, notes, dict(data=None, inEditMode=False, isDirty=False),dash.no_update, dash.no_update

