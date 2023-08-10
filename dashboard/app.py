from functools import partial

import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import Output, Input, html, dcc, ALL, State
from dash_iconify import DashIconify

from dashboard.components.button.buttons import control_buttons
from dashboard.components.chart_drawer.drawer import chart_drawer
from dashboard.components.chart_drawer.types.audio import create_audio_chart
from dashboard.components.chart_drawer.types.env import create_env_chart
from dashboard.components.chart_drawer.types.environment import create_environment_chart
from dashboard.components.chart_drawer.types.pax import create_pax_chart
from dashboard.components.chart_drawer.types.pollinator import create_pollinator_chart
from dashboard.components.map.init_map import map_figure
from dashboard.components.map.layer_selection.drawer import map_menu_drawer
from dashboard.components.map.layer_selection.popup import map_menu_popup
from dashboard.components.settings_drawer.drawer import settings_drawer
from dashboard.config.app import app_theme, SETTINGS_DRAWER_WIDTH
from dashboard.config.id import *
from dashboard.init import init_deployment_data, init_environment_data
from dashboard.maindash import app
from util.functions import safe_reduce

deployments, deployment_markers, tags = init_deployment_data()
environments, environment_legend = init_environment_data()

style_hidden = {"visibility": "hidden"}
style_visible = {"visibility": "visible"}

chart_supported_devices = {
    "Env. Sensor": create_env_chart,
    "Pax Counter": create_pax_chart,
    "Audio Logger": create_audio_chart,
    "Pollinator Cam": create_pollinator_chart,
    "Environment": partial(create_environment_chart, environment_legend)
}


def create_notification(title, message):
    return dmc.Notification(
        title=title,
        id=f"id-notification-{title}",
        action="show",
        message=message,
        icon=DashIconify(icon="material-symbols:circle-notifications", height=24),
    )


app_content = [
    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
    dcc.Store(id=ID_DEPLOYMENT_DATA_STORE, data=deployments),
    dcc.Store(id=ID_TAG_DATA_STORE, data=tags),
    dcc.Store(id=ID_ENV_DATA_STORE, data=environments),
    dcc.Store(id=ID_DEPLOYMENT_MARKER_STORE, data=deployment_markers),
    dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(clicks=None)),
    dcc.Store(id=ID_BASE_MAP_STORE, data=dict(), storage_type="local"),
    dcc.Store(id=ID_OVERLAY_MAP_STORE, data=dict(), storage_type="local"),
    dcc.Store(id=ID_CURRENT_CHART_DATA_STORE, data=dict(role=None, id=None)),
    dcc.Store(id=ID_ENVIRONMENT_LEGEND_STORE, data=environment_legend),
    html.Div(id=ID_NOTIFICATION_CONTAINER),
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
    dmc.MediaQuery(
        map_menu_popup("menu"),
        smallerThan="sm",
        styles=style_hidden
    ),

    dmc.Drawer(
        map_menu_drawer("drawer"),
        id=ID_BOTTOM_DRAWER,
        size="lg",
        zIndex=90000,
    ),
    *control_buttons(),
    chart_drawer(),
    settings_drawer(deployments, tags, deployment_markers)
]


discover_app = dmc.MantineProvider(
    id=ID_APP_THEME,
    theme=app_theme,
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        dmc.NotificationsProvider(
            html.Div(
                children=app_content,
                id=ID_APP_CONTAINER,
            )
        ),
    ]
)

app.layout = discover_app


@app.callback(
    Output(ID_NOTES_LAYER_GROUP, "children"),
    Input(ID_MAP, "dbl_click_lat_lng"),
    State(ID_MAP, "boundsOptions"),
    State(ID_NOTES_LAYER_GROUP, "children"),
    prevent_initial_call=True
)
def handle_double_click(click, bounds, markers):
    marker = dl.Marker(
        position=[click[0], click[1]],
        icon=dict(iconUrl="assets/markers/note.svg", iconAnchor=[15, 6], iconSize=30),
    )
    if markers is None:
        markers = []
    return [*markers, marker]


@app.callback(
    Output(ID_URL_LOCATION, "search"),
    Input(ID_MAP, "click_lat_lng"),
    Input(ID_MAP, "zoom"),
    prevent_initial_call=True
)
def map_click(click_lat_lng, zoom):
    loc = ""
    if click_lat_lng is not None:
        loc = [f"?lat={click_lat_lng[0]}&lon={click_lat_lng[1]}&zoom={zoom}"]
    return loc


@app.callback(
    Output(ID_MAP_CONTAINER, "style"),
    Output(ID_CHART_DRAWER, "styles"),
    Input(ID_SETTINGS_DRAWER, "opened")
)
def settings_drawer_state(state):
    width_reduced = {"width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}
    full_width = {"width": "100vw"}
    if state:
        return width_reduced, {"drawer": {"left": "400px", "width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}}
    return full_width, {"drawer": {"left": "0", "width": "100vw"}}


@app.callback(
    Output(ID_CHART_DRAWER, "opened"),
    Output(ID_CHART_DRAWER, "position"),
    Output(ID_MARKER_CLICK_STORE, "data"),
    Output(ID_CURRENT_CHART_DATA_STORE, "data"),
    Output(ID_NOTIFICATION_CONTAINER, "children"),
    Input({"role": ALL, "id": ALL, "label": ALL}, "n_clicks"),
    State(ID_MARKER_CLICK_STORE, "data"),
    State(ID_CURRENT_CHART_DATA_STORE, "data"),
    prevent_initial_call=True,
)
def marker_click(n_clicks, data, chart_data):
    # determine whether the callback is triggered by a click
    # necessary, because adding markers to the map triggers the callback
    click_sum = safe_reduce(lambda x, y: x + y, n_clicks)
    has_click_triggered = False

    if click_sum is not None:
        has_click_triggered = click_sum != data["clicks"]
        data["clicks"] = click_sum

    open_drawer = False
    notification = None
    if has_click_triggered and dash.ctx.triggered_id is not None:
        trigger_id = dash.ctx.triggered_id
        if trigger_id["role"] not in chart_supported_devices.keys():
            notification = create_notification(trigger_id["role"], "No further data available!")
        else:
            chart_data = dict(role=trigger_id["role"], id=trigger_id["id"])
            open_drawer = True

    return open_drawer, "bottom", data, chart_data, notification


@app.callback(
    Output(ID_CHART_CONTAINER, "children"),
    Input(ID_CURRENT_CHART_DATA_STORE, "data"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def display_chart(data, theme):
    deployment_id = data["id"]
    new_figure = html.Div()
    device_type = data["role"]
    if device_type in chart_supported_devices.keys():
        fn = chart_supported_devices[device_type]
        new_figure = fn(deployment_id, theme)

    return new_figure
