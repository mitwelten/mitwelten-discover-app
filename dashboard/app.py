import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import Output, Input, html, dcc, State

from dashboard.components.button.buttons import control_buttons
from dashboard.components.chart_drawer.drawer import chart_drawer
from dashboard.components.map.init_map import map_figure
from dashboard.components.map.menus import map_layer_menus
from dashboard.components.settings_drawer.drawer import settings_drawer
from dashboard.config.app import app_theme
from dashboard.config.chart import get_supported_chart_types
from dashboard.config.id import *
from dashboard.init import init_deployment_data, init_environment_data
from dashboard.maindash import app

deployments, deployment_markers, tags = init_deployment_data()
environments, environment_legend = init_environment_data()


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
    *map_layer_menus(),
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
    Output(ID_CHART_CONTAINER, "children"),
    Input(ID_CURRENT_CHART_DATA_STORE, "data"),
    State(ID_APP_THEME, "theme"),
    State(ID_ENVIRONMENT_LEGEND_STORE, "data"),
    prevent_initial_call=True
)
def display_chart(data, theme, legend):
    deployment_id = data["id"]
    new_figure = html.Div()
    device_type = data["role"]
    if device_type in get_supported_chart_types().keys():
        fn = get_supported_chart_types(legend)[device_type]
        new_figure = fn(deployment_id, theme)

    return new_figure
