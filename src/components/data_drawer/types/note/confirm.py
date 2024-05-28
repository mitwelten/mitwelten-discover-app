from dash import Output, Input, State, no_update, dcc
import flask
import dash_mantine_components as dmc
from http.client import responses

from src.api.api_note import delete_note
from src.main import app
from dash.exceptions import PreventUpdate
from src.config.id_config import *
from src.config.app_config import (
    CONFIRM_UNSAVED_CHANGES_MESSAGE,
    CONFIRM_DELETE_MESSAGE,
)

confirm_dialogs = [
            dcc.ConfirmDialog(
                id=ID_CONFIRM_UNSAVED_CHANGES_DIALOG, 
                message=CONFIRM_UNSAVED_CHANGES_MESSAGE
                ),
            dcc.ConfirmDialog(
                id=ID_CONFIRM_DELETE_DIALOG, 
                message=CONFIRM_DELETE_MESSAGE
                ),
            ]


@app.callback(
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "is_open", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "children", allow_duplicate=True),
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Input(ID_CONFIRM_DELETE_DIALOG, "submit_n_clicks"),
    State(ID_EDIT_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def deactivate_edit_mode_from_delete(delete_click, note):
    if delete_click is None or delete_click == 0:
        raise PreventUpdate

    auth_cookie = flask.request.cookies.get("auth")
    response = delete_note(note["data"]["id"], auth_cookie)
    if response == 200:
        return dict(data=None), False, no_update, no_update, dict(entries=[], type="Note")
    else:
        notification = [
            dmc.Title("Something went wrong!", order=6),
            dmc.Text("Could not delete Note."),
            dmc.Text(f"Exited with Status Code: {response} | {responses[response]}", color="dimmed")
        ]
        return no_update, no_update, True, notification, no_update



