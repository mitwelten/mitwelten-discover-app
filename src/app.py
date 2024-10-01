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
    clientside_callback,
    ClientsideFunction
)
from dash.exceptions import PreventUpdate
from configuration import DOMAIN_NAME

from src.model.base import BaseDeployment
from src.model.url_parameter import UrlParameter
from src.components.button.buttons import floating_buttons
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
from src.components.map.legende_lebensraumkarte import legende_lebensraumkarte
from src.main import app
from src.data.init import init_deployment_data, init_environment_data, init_notes, init_tags
from src.url.parse import update_query_data, query_data_to_string
import flask
from src.url.parse import get_device_from_params

def app_content(args):

    # initialize data from backend
    cookies      = flask.request.cookies

    envs, legend = init_environment_data()
    env_data     = dict(entries=envs, legend=legend)
    notes        = init_notes(cookies.get("auth") if cookies else None)
    tags         = init_tags()
    deployments  = init_deployment_data()
    url_params   = UrlParameter(args)
    active_depl: BaseDeployment | None = get_device_from_params(url_params, deployments, notes, envs)
    print("---")
    print(active_depl)
    print("---")

    return [
            dcc.Interval(id=ID_STAY_LOGGED_IN_INTERVAL, interval=30 * 1000, disabled=True),
            mitwelten_bannner,
            legende_lebensraumkarte,
            *stores(url_params, deployments, notes, env_data, tags, active_depl),
            *floating_buttons,
            map_figure(url_params, active_depl),
            chart_drawer(url_params, active_depl, notes, env_data),
            settings_drawer(url_params, tags, active_depl, deployments),
            html.Div(id=ID_NOTIFICATION),
        ]


def discover_app(**kwargs): 
    return dmc.MantineProvider(
            forceColorScheme="light",
            id=ID_APP_THEME,
            theme=app_theme,
            children=[
                dmc.NotificationProvider(position="bottom-right"),
                html.Div(
                    id=ID_APP_CONTAINER,
                    children=[
                        *app_content(kwargs),
                        dcc.Location(id=ID_URL_LOCATION, refresh=False),
                        ], 
                    ),
                ]
            )

register_page("Mitwelten Discover", layout=discover_app, path="/", title="Mitwelten Discover")


@app.callback(
    Output(ID_STAY_LOGGED_IN_INTERVAL, "interval"),
    Output(ID_LOGIN_AVATAR_CONTAINER, "n_clicks"),
    Input(ID_STAY_LOGGED_IN_INTERVAL, "n_intervals"),
    State(ID_LOGIN_AVATAR_CONTAINER, "n_clicks"),
    prevent_initial_call=True,
)
def backend_request_to_stay_logged_in(_, avatar_clicks):
    exp = get_expiration_date_from_cookies()
    if exp is None or exp - time.time() < 0:
        return no_update, avatar_clicks + 1 if avatar_clicks is not None else 0
    raise PreventUpdate

@app.callback(
    Output(ID_URL_LOCATION, "search", allow_duplicate=True),
    Output(ID_LOGIN_BUTTON_HREF, "href"),
    Input(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
    )
def update_url_of_login_logout_button(data):
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
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_MAP, "clickData"),
    State(ID_EDIT_NOTE_STORE, "data"),
    State(ID_CHART_DRAWER, "opened"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
)
def map_click(_, selected_note, drawer_state, data):
    if selected_note["data"] is not None or not drawer_state:
        raise PreventUpdate

    new_data = update_query_data(
            data, { 
             "node_label": None,
             "env_id": None,
             "note_id": None,
             }
            )

    note_store = no_update if selected_note["data"] is None else dict(data=None)
    return False, note_store, new_data


@app.callback(
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_MAP, "center"),
    Input(ID_MAP, "zoom"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
)
def update_map_center_in_url(center, zoom, data):
    if ctx.triggered_id is None:
        raise PreventUpdate

    return update_query_data(
            data, { 
             "lat": center["lat"],
             "lon": center["lng"],
             "zoom": int(zoom)
             }
            )


clientside_callback(
    ClientsideFunction(
        namespace="util", function_name="getTimezone"
    ),
    Output(ID_TIMEZONE_STORE, "data"),
    Input(ID_TIMEZONE_STORE, "data"),
)

