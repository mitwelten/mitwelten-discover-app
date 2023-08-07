from urllib.parse import urlparse, parse_qs

import dash
import dash_mantine_components as dmc
from dash import Output, Input, html, dcc, ALL, State

from dashboard.components.action_button import action_button
from dashboard.components.data_chart.devices.env import create_env_chart
from dashboard.components.data_chart.devices.pax import create_pax_chart
from dashboard.components.left_drawer.settings import settings_content
from dashboard.components.map.init_map import map_figure
from dashboard.components.map.map_layer_selection import map_menu_popup, map_menu_drawer
from dashboard.config import map_config
from dashboard.config.app_config import app_theme
from dashboard.config.id_config import *
from dashboard.init import init_app_data
from dashboard.maindash import app
from util.functions import safe_reduce

deployments, colors,  tags = init_app_data()


style_hidden = {"visibility": "hidden"}
style_visible = {"visibility": "visible"}

app_content = [
    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
    dcc.Store(id=ID_DEPLOYMENT_DATA_STORE, data=deployments),
    dcc.Store(id=ID_TAG_DATA_STORE, data=tags),
    dcc.Store(id=ID_DEPLOYMENT_COLOR_STORE, data=colors),
    dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(clicks=None)),
    dcc.Store(id=ID_BASE_MAP_STORE, data=dict(), storage_type="local"),
    dcc.Store(id=ID_OVERLAY_MAP_STORE, data=dict(), storage_type="local"),
    dcc.Store(id=ID_CURRENT_CHART_DATA, data=dict(role=None, id=None)),
    map_figure,
    dmc.MediaQuery(
        action_button(button_id=ID_BOTTOM_DRAWER_BUTTON, icon="material-symbols:layers-outline"),
        largerThan="sm",
        styles=style_hidden
    ),
    dmc.MediaQuery(
        map_menu_popup("menu"),
        smallerThan="sm",
        styles=style_hidden
    ),

    action_button(button_id=ID_OPEN_LEFT_DRAWER_BUTTON, icon="material-symbols:menu"),
    dmc.Drawer(
        map_menu_drawer("drawer"),
        id=ID_BOTTOM_DRAWER,
        size="lg",
        zIndex=10000,
    ),
    dmc.Drawer(
        opened=False,
        id=ID_CHART_DRAWER,
        zIndex=20000,
        size="50%",
        closeOnClickOutside=False,
        closeOnEscape=False,
        withOverlay=False,
        className="chart-drawer",
        children=[
            dmc.LoadingOverlay(
                html.Div(id=ID_CHART_CONTAINER, className="measurement-chart"),
                loaderProps={"variant": "dots", "color": "orange", "size": "xl"},
            )
        ]
    ),
    dmc.Drawer(
        id=ID_LEFT_DRAWER,
        children=settings_content(deployments, tags, colors),
        opened=True,
        size=400,
        padding="md",
        closeOnClickOutside=False,
        closeOnEscape=False,
        withOverlay=False,
        zIndex=90000,
    ),
]


discover_app = dmc.MantineProvider(
    id=ID_APP_THEME,
    theme=app_theme,
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        html.Div(
            children=app_content,
            id=ID_APP_CONTAINER,
        ),
    ]
)

app.layout = discover_app


@app.callback(
    Output(ID_MAP, 'center'),
    Output(ID_MAP, 'zoom'),
    Input(ID_URL_LOCATION, 'href'),
)
def display_page(href):
    lat = map_config.DEFAULT_LAT
    lon = map_config.DEFAULT_LON
    zoom = map_config.DEFAULT_ZOOM
    query = urlparse(href).query
    query_params: dict = parse_qs(query)
    if query_params:
        lat = query_params["lat"][0]
        lon = query_params["lon"][0]
        zoom = query_params["zoom"][0]

    return (lat, lon), zoom


# @app.callback(
#     Output(ID_LOADER, "children"),
#     Input(ID_MAP, "dbl_click_lat_lng")
# )
# def handle_double_click(click):
#     print("double clicked")
#     return dash.no_update


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
    Output(ID_BOTTOM_DRAWER, "opened", allow_duplicate=True),
    Output(ID_BOTTOM_DRAWER, "position", allow_duplicate=True),
    Input(ID_BOTTOM_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_bottom_drawer(_):
    return True, "bottom"


@app.callback(
    Output(ID_BOTTOM_DRAWER, "opened", allow_duplicate=True),
    Output(ID_BOTTOM_DRAWER, "position", allow_duplicate=True),
    Input(ID_MAP, "click_lat_lng"),
    Input({'role': ALL, 'index': ALL, 'place': "drawer"}, 'n_clicks'),
    prevent_initial_call=True,
)
def open_bottom_drawer(_1, _2):
    return False, "bottom"


@app.callback(
    Output(ID_LEFT_DRAWER, "opened"),
    Output(ID_LEFT_DRAWER, "position"),
    Input(ID_OPEN_LEFT_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_left_drawer(_):
    return True, "left"


@app.callback(
    Output(ID_CHART_DRAWER, "opened"),
    Output(ID_CHART_DRAWER, "position"),
    Output(ID_MARKER_CLICK_STORE, "data"),
    Output(ID_CURRENT_CHART_DATA, "data"),
    Input({"role": ALL, "development_id": ALL, "label": ALL}, "n_clicks"),
    State(ID_MARKER_CLICK_STORE, "data"),
    State(ID_CURRENT_CHART_DATA, "data"),
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
    if has_click_triggered and dash.ctx.triggered_id is not None:
        trigger_id = dash.ctx.triggered_id
        chart_data = dict(role=trigger_id["role"], id=trigger_id["development_id"])
        open_drawer = True

    return open_drawer, "bottom", data, chart_data


@app.callback(
    Output(ID_CHART_CONTAINER, "children"),
    Input(ID_CURRENT_CHART_DATA, "data"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def display_chart(data, theme):
    deployment_id = data["id"]
    match data["role"]:
        case "Env. Sensor": new_figure = create_env_chart(deployment_id, theme)
        case "Pax Counter": new_figure = create_pax_chart(deployment_id, theme)
        case _: new_figure = dmc.Center(dmc.Text("No Data available", color="dimmed"))

    return new_figure
