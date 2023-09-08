from functools import partial

import dash
from dash import dcc
from dash.exceptions import PreventUpdate

from dashboard.components.button.buttons import control_buttons
from dashboard.components.data_drawer.data_drawer import chart_drawer
from dashboard.components.data_drawer.types.pollinator import *
from dashboard.components.map.init_map import map_figure
from dashboard.components.settings_drawer.drawer import settings_drawer
from dashboard.config.app import app_theme, DATA_SOURCES_WITHOUT_CHART_SUPPORT
from dashboard.config.map import DEFAULT_LAT, DEFAULT_LON
from dashboard.init import init_deployment_data, init_environment_data, init_notes
from util.functions import safe_reduce

deployments, data_sources, tags = init_deployment_data()
environments, environment_legend = init_environment_data()
notes = init_notes()

app_content = [
    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
    dcc.Store(id=ID_DEPLOYMENT_DATA_STORE, data=deployments),
    dcc.Store(id=ID_NOTES_STORE, data=notes, storage_type="local"),
    dcc.Store(id=ID_TAG_DATA_STORE, data=tags),
    dcc.Store(id=ID_ENV_DATA_STORE, data=environments),
    dcc.Store(id=ID_DATA_SOURCE_STORE, data=data_sources),
    dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(clicks=None), storage_type="local"),
    dcc.Store(id=ID_BASE_MAP_STORE, data=dict(index=0), storage_type="local"),
    dcc.Store(id=ID_OVERLAY_MAP_STORE, data=dict(index=0), storage_type="local"),
    dcc.Store(id=ID_CURRENT_DRAWER_DATA_STORE, data=dict(role=None, id=None, location=None)),
    dcc.Store(id=ID_ENVIRONMENT_LEGEND_STORE, data=environment_legend),
    dcc.Store(id=ID_FOCUS_ON_MAP_LOCATION, data=dict(lat=DEFAULT_LAT, lon=DEFAULT_LON)),
    dcc.Store(id=ID_NEW_NOTE_STORE, data=[]),
    dcc.Store(id=ID_PREVENT_MARKER_EVENT, data=dict(state=False)),
    dcc.Store(id=ID_EDIT_NOTE_STORE, data=dict(id=None)),
    dcc.Store(id=ID_SELECTED_NOTE_STORE, data=None),

    html.Div(
        html.A(
            "MITWELTEN",
            title="mitwelten.org",
            href="https://mitwelten.org",
            target="_blank",
            className="mitwelten-logo"
        ),
        id=ID_MAP_CONTAINER,
    ),

    map_figure,
    chart_drawer(),
    *control_buttons(),
    settings_drawer(deployments, tags, data_sources),
    dmc.Modal(id=ID_NOTE_ATTACHMENT_MODAL, size="lg", opened=False, zIndex=30000),
]


discover_app = dmc.MantineProvider(
    id=ID_APP_THEME,
    theme=app_theme,
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        dmc.NotificationsProvider([
            html.Div(
                children=app_content,
                id=ID_APP_CONTAINER,
            ),
            html.Div(id=ID_NOTIFICATION_CONTAINER),
        ],
            zIndex=9999999
        ),
    ]
)

app.layout = discover_app


@app.callback(
    Output(ID_URL_LOCATION, "search"),
    Input(ID_MAP, "click_lat_lng"),
    Input(ID_MAP, "zoom"),
    prevent_initial_call=True
)
def map_click(click_lat_lng, zoom):
    loc = ""
    if click_lat_lng is not None:
        loc = f"?lat={click_lat_lng[0]}&lon={click_lat_lng[1]}&zoom={zoom}"
    return loc


def handle_marker_click(data_source, marker_click, data, prevent_event):
    if prevent_event["state"]:
        raise PreventUpdate

    trigger = dash.ctx.triggered_id
    if trigger is None:
        raise PreventUpdate

    # required to determine if a click occurred (callback is fired when a marker is added to the map as well)
    click_sum = safe_reduce(lambda x, y: x + y, marker_click)
    has_click_triggered = False
    if click_sum is not None:
        has_click_triggered = click_sum != data["clicks"]
        data["clicks"] = click_sum

    if has_click_triggered:
        return data, dict(role=data_source, id=trigger["id"], lat=trigger["lat"], lon=trigger["lon"])

    return dash.no_update, dash.no_update


for source in data_sources:
    app.callback(
        Output(ID_MARKER_CLICK_STORE, "data", allow_duplicate=True),
        Output(ID_CURRENT_DRAWER_DATA_STORE, "data", allow_duplicate=True),
        Input({"role": source, "id": ALL, "label": "Node", "lat": ALL, "lon": ALL}, "n_clicks"),
        State(ID_MARKER_CLICK_STORE, "data"),
        State(ID_PREVENT_MARKER_EVENT, "data"),
        prevent_initial_call=True
    )(partial(handle_marker_click, source))




