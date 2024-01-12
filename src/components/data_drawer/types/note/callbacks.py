import dash
from dash import Output, Input, State
from dash.exceptions import PreventUpdate

import dash_mantine_components as dmc
from src.config.id_config import *
from src.main import app
from src.model.note import Note, empty_note
from src.util.user_validation import get_user_from_cookies


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
    Input(ID_ADD_NOTE_BUTTON, "n_clicks"),
    State(ID_BROWSER_PROPERTIES_STORE, "data"),
    State(ID_SETTINGS_DRAWER, "opened"),
    State(ID_SETTINGS_DRAWER, "size"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_MAP, "bounds"),

    prevent_initial_call=True
)
def create_note_on_map(
        click, 
        browser_props, 
        drawer_state,
        settings_drawer_size,
        data_drawer_size,
        bounds
    ):
    user = get_user_from_cookies()

    if user is None:
        notification = [
            dmc.Title("Operation not permitted", order=6),
            dmc.Text("Log in to create notes!")
        ]
        return dash.no_update, True, notification

    new_note = Note(empty_note)
    if click is None or click == 0:
        raise PreventUpdate
    else:
        top    = bounds[1][0]
        bottom = bounds[0][0]
        left   = bounds[0][1]
        right  = bounds[1][1]

        # visibile map distance in grad
        map_delta_lat = top - bottom
        map_delta_lon = right - left

        # set drawer size to 1 if the settings drawer is closed
        settings_drawer_size = 0 if not drawer_state else settings_drawer_size

        # the height of the data drawer in grad
        data_drawer_height = map_delta_lat   / browser_props["height"] * data_drawer_size

        # the width of the settings drawer in grad
        settings_drawer_width = map_delta_lon / browser_props["width"]  * settings_drawer_size

        new_note.lon = left + settings_drawer_width + ((map_delta_lon - settings_drawer_width) / 2)
        new_note.lat = bottom + data_drawer_height + ((map_delta_lat - data_drawer_height) / 2)

    new_note = new_note.to_dict()
    return dict(data=new_note, type="Note"), dash.no_update, dash.no_update
