import time
from functools import partial

import dash_mantine_components as dmc
import dash_core_components as dcc
from dash import (
    register_page,
    ALL,
    html,
    Output,
    Input,
    State, 
    ctx,
    no_update,
)
from dash.exceptions import PreventUpdate
from src.components.data_drawer.types.note.note_view import note_view
from configuration import DOMAIN_NAME

from src.components.alert.alert import alert_danger, alert_warning, alert_info
from src.model.note import Note
from src.components.button.buttons import control_buttons
from src.config.id_config import *
from src.components.map.init_map import map_figure
from src.components.map.banner import mitwelten_bannner
from src.components.settings_drawer.settings_drawer import settings_drawer
from src.components.data_drawer.data_drawer import chart_drawer
from src.config.app_config import (
    app_theme,
    CONFIRM_UNSAVED_CHANGES_MESSAGE,
    CONFIRM_DELETE_MESSAGE,
)
from src.config.map_config import SOURCE_PROPS
from src.data.stores import stores
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_expiration_date_from_cookies
from src.main import app
from src.data.init import init_deployment_data, init_environment_data, init_notes
from src.util.util import query_data_to_string, update_query_data
import flask


def get_device_from_args(args, deployments):
    active_id = args.get("id", None)
    active_depl = None
    #if active_id is not None:
    #    for depl in deployments.values():
    #        for d in depl:
    #            if d["id"] == int(active_id):
    #                active_depl = d  
    #                break
    return active_depl


def app_content(args):

    cookies      = flask.request.cookies
    notes        = init_notes(cookies["auth"] if cookies else None)

    data, legend = init_environment_data()
    env_data     = {"entries": data, "legend": legend}

    deployments  = init_deployment_data()
    active_depl  = get_device_from_args(args, deployments)

    return [
    dcc.Interval(id=ID_STAY_LOGGED_IN_INTERVAL, interval=30 * 1000, disabled=True),
    alert_danger,
    alert_warning,
    alert_info,
    mitwelten_bannner,

    dcc.ConfirmDialog(
        id=ID_CONFIRM_UNSAVED_CHANGES_DIALOG, 
        message=CONFIRM_UNSAVED_CHANGES_MESSAGE
    ),
    dcc.ConfirmDialog(
        id=ID_CONFIRM_DELETE_DIALOG, 
        message=CONFIRM_DELETE_MESSAGE
    ),

    *stores(args, deployments, notes, env_data),
    *control_buttons,
    map_figure(args, active_depl),
    chart_drawer(args, active_depl, notes, env_data),
    settings_drawer(args),
]

attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

def discover_app(**kwargs): 
    print("app args: ", kwargs)
    return dmc.MantineProvider(
    id=ID_APP_THEME,
    theme=app_theme,
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        html.Div(
            id=ID_APP_CONTAINER,
            children=[
                dcc.Location(id=ID_URL_LOCATION, refresh=False),
                *app_content(kwargs)
                ], 
            ),
    ],
)

register_page("home", layout=discover_app, path="/")
#app.layout = discover_app



@app.callback(
    Output(ID_STAY_LOGGED_IN_INTERVAL, "interval"),
    Output(ID_LOGIN_AVATAR_CONTAINER, "n_clicks"),
    Input(ID_STAY_LOGGED_IN_INTERVAL, "n_intervals"),
    State(ID_LOGIN_AVATAR_CONTAINER, "n_clicks"),
    prevent_initial_call=True,
)
def create_backend_request_to_stay_logged_in(_, avatar_clicks):
    exp = get_expiration_date_from_cookies()
    if exp is None or exp - time.time() < 0:
        return no_update, avatar_clicks + 1 if avatar_clicks is not None else 0
    raise PreventUpdate


@app.callback(
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_MAP, "clickData"),
    State(ID_MAP, "zoom"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
)
def map_click_handle(click_data, zoom, data):
    if click_data is None:
        raise PreventUpdate

    location = click_data["latlng"]
    return update_query_data(data,
                             { "zoom": zoom,
                              "lat": location["lat"],
                              "lon": location["lng"],
                              "node_label": None
                              }
                             )


@app.callback(
    Output(ID_URL_LOCATION, "search", allow_duplicate=True),
    Output(ID_LOGIN_BUTTON_HREF, "href"),
    Input(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
    )
def update_url(data):
    query_params = query_data_to_string(data)
    login_url = f"{DOMAIN_NAME}/login{query_params}" 
    return query_params, login_url


def handle_marker_click(data_source, marker_click, prevent_event, store, clickdata):
    if prevent_event["state"]:
        raise PreventUpdate

    click_sum = safe_reduce(lambda x, y: x + y, marker_click, 0)
    if click_sum == 0 or ctx.triggered_id is None:
        raise PreventUpdate

    for entry in store[0]["entries"]:
        if entry["id"] == ctx.triggered_id["id"]:
            return dict(data=entry, type=data_source)

    raise PreventUpdate


for source in SOURCE_PROPS.keys():
    app.callback(
        Output(ID_SELECTED_MARKER_STORE, "data", allow_duplicate=True),
        Input({"role": source, "id": ALL, "label": "Node"}, "n_clicks"),
        State(ID_PREVENT_MARKER_EVENT, "data"),
        State({"role": source, "label": "Store", "type": ALL}, "data"),
        State({"role": source, "id": ALL, "label": "Node"}, "clickData"),
        prevent_initial_call=True,
    )(partial(handle_marker_click, source))


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_MAP, "clickData"),
    State(ID_EDIT_NOTE_STORE, "data"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    prevent_initial_call=True,
)
def map_click(_, selected_note, notes):
    if selected_note["data"] is not None:
        for note in notes["entries"]:
            if note["id"] == selected_note["data"]["id"]:
                if Note(note) != Note(selected_note["data"]):
                    return no_update, True, no_update

    return False, no_update, dict(data=None)


@app.callback(
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_NOTE_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Input(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "submit_n_clicks"),
    State(ID_EDIT_NOTE_STORE, "data"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True,
)
def deactivate_edit_mode(cancel_click, selected_note, notes, drawer_size, theme):
    if cancel_click is None or cancel_click == 0:
        return no_update, no_update, True, no_update
    
    for note in notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            n = Note(note)
            file_height = 116 if len(n.files) > 3 else 50 if len(n.files) > 0 else 0
            drawer_size -= 116 - file_height                    
            return dict(data=None), drawer_size, True, note_view(n, file_height, theme), True

