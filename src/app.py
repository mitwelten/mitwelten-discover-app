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
from configuration import DOMAIN_NAME

from src.components.alert.alert import alert_danger, alert_warning, alert_info
from src.components.button.buttons import control_buttons
from src.config.id_config import *
from src.components.map.init_map import map_figure
from src.components.map.banner import mitwelten_bannner
from src.components.settings_drawer.settings_drawer import settings_drawer
from src.components.data_drawer.data_drawer import chart_drawer
from src.config.app_config import app_theme
from src.config.map_config import SOURCE_PROPS
from src.data.stores import stores
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_expiration_date_from_cookies
from src.main import app
from src.data.init import init_deployment_data, init_environment_data, init_notes
from src.url.parse import update_query_data, query_data_to_string
import flask
from src.url.parse import get_device_from_args
from src.url.default import set_default_args


def app_content(args):

    # initialize data from backend
    cookies      = flask.request.cookies
    notes        = init_notes(cookies["auth"] if cookies else None)

    environments, legend = init_environment_data()
    env_data     = {"entries": environments, "legend": legend}

    deployments  = init_deployment_data()
    active_depl  = None

    active_depl  = get_device_from_args(args, deployments, notes, environments)

    # render app content
    return [
            dcc.Interval(id=ID_STAY_LOGGED_IN_INTERVAL, interval=30 * 1000, disabled=True),
            alert_danger, alert_warning, alert_info,
            mitwelten_bannner,
            *stores(args, deployments, notes, env_data),
            *control_buttons,
            map_figure(args, active_depl),
            chart_drawer(args, active_depl, notes, env_data),
            settings_drawer(args),
            ]


def discover_app(**kwargs): 
    print("app kwargs: ", kwargs)
    args = set_default_args(kwargs)
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
                        *app_content(args)
                        ], 
                    ),
                ],
            )

register_page("Discover", layout=discover_app, path="/")


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
def update_query_data_location(click_data, zoom, data):
    if click_data is None:
        raise PreventUpdate

    location = click_data["latlng"]
    return update_query_data(
            data,
            { "zoom": zoom,
             "lat": location["lat"],
             "lon": location["lng"],
             "node_label": None,
             "note_id": None,
             "env_id": None,
             }
            )


@app.callback(
    Output(ID_URL_LOCATION, "search", allow_duplicate=True),
    Output(ID_LOGIN_BUTTON_HREF, "href"),
    Input(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
    )
def update_url_of_login_logout_button(data):
    query_params = query_data_to_string(data)
    print("update_url_of_login_logout_button: ", query_params)
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
            return dict(data=entry, type=data_source), None

    raise PreventUpdate


for source in SOURCE_PROPS.keys():
    app.callback(
        Output(ID_SELECTED_MARKER_STORE, "data", allow_duplicate=True),
        Output(ID_INIT_POPUP_LAYER, "children", allow_duplicate=True),
        Input({"role": source, "id": ALL, "label": "Node"}, "n_clicks"),
        State(ID_PREVENT_MARKER_EVENT, "data"),
        State({"role": source, "label": "Store", "type": ALL}, "data"),
        State({"role": source, "id": ALL, "label": "Node"}, "clickData"),
        prevent_initial_call=True,
    )(partial(handle_marker_click, source))


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_MAP, "clickData"),
    State(ID_EDIT_NOTE_STORE, "data"),
    prevent_initial_call=True,
)
def map_click(_, selected_note):
    if selected_note["data"] is not None:
        raise PreventUpdate

    return False, dict(data=None)



