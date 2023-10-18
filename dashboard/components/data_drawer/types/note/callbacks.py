import dash
from dash import Output, Input, State
from dash.exceptions import PreventUpdate

import dash_mantine_components as dmc
from dashboard.config.id_config import *
from dashboard.maindash import app
from dashboard.model.note import Note, empty_note
from dashboard.util.user_validation import get_user_from_cookies


@app.callback(
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def activate_preventing_marker_clicks(selected_note):
    return dict(state=selected_note["inEditMode"])


@app.callback(
    Output(ID_SELECTED_MARKER_STORE, "data", allow_duplicate=True),
    Output(ID_ALERT_INFO, "is_open", allow_duplicate=True),
    Output(ID_ALERT_INFO, "children", allow_duplicate=True),
    Input(ID_MAP, "dblclickData"),
    Input(ID_ADD_NOTE_BUTTON, "n_clicks"),
    State(ID_MAP, "center"),
    prevent_initial_call=True
)
def create_note_on_map(click_location, click, center):
    user = get_user_from_cookies()

    if user is None:
        notification = [
            dmc.Title("Operation not permitted", order=6),
            dmc.Text("Log in to create notes!")
        ]
        return dash.no_update, True, notification

    new_note = Note(empty_note)
    if dash.ctx.triggered_id == ID_ADD_NOTE_BUTTON:
        if click is None or click == 0:
            raise PreventUpdate
        else:
            new_note.lat = center.get("lat", 0)
            new_note.lon = center.get("lng", 0)
    else:
        # double-click on map occurred
        new_note.lat = click_location["latlng"]["lat"]
        new_note.lon = click_location["latlng"]["lng"]

    new_note = new_note.to_dict()
    return dict(data=new_note, type="Note"), dash.no_update, dash.no_update
