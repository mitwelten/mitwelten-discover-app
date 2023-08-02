from urllib.parse import urlparse, parse_qs

import dash
import dash_mantine_components as dmc
import plotly.express as px
from dash import Output, Input, html, dcc, ALL, State

from dashboard.components.action_button import action_button
from dashboard.components.data_chart.chart import create_env_chart, create_pax_chart
from dashboard.components.left_drawer.settings import settings_content
from dashboard.components.map.init_map import map_figure
from dashboard.components.map.map_layer_selection import map_menu_popup, map_menu_drawer
from dashboard.config import map_config
from dashboard.config.id_config import *
from dashboard.init import init_app_data
from dashboard.maindash import app
from util.functions import safe_reduce

deployments, colors,  tags = init_app_data()


fig = px.line()

graph = dmc.Container(
    dcc.Graph(
        id=ID_MEASUREMENT_CHART,
        figure=fig,
        config={"displayModeBar": False},
        className="measurement-chart",
    ),
)

app_content = [
    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
    dcc.Store(id=ID_DEPLOYMENT_DATA_STORE, data=deployments),
    dcc.Store(id=ID_TAG_DATA_STORE, data=tags),
    dcc.Store(id=ID_DEPLOYMENT_COLOR_STORE, data=colors),
    dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(clicks=None)),
    dcc.Store(id=ID_BASE_MAP_STORE, data=dict(index=1)),
    dcc.Store(id=ID_OVERLAY_MAP_STORE, data=dict(index=4)),
    dcc.Store(id=ID_CURRENT_CHART_DATA, data=dict(role=None, id=None)),


    map_figure,

    dmc.MediaQuery(
        action_button(button_id=ID_BOTTOM_DRAWER_BUTTON, icon="material-symbols:layers-outline"),
        largerThan="sm",
        styles={"visibility": "hidden"}
    ),
    dmc.MediaQuery(
        map_menu_popup("menu"),
        smallerThan="sm",
        styles={"visibility": "hidden"}
    ),

    action_button(button_id=ID_OPEN_LEFT_DRAWER_BUTTON, icon="material-symbols:menu"),
    dmc.Drawer(
        map_menu_drawer("drawer"),
        id=ID_BOTTOM_DRAWER,
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
        children=[
            dmc.Loader(
                id=ID_LOADER,
                color="blue",
                size="lg",
                variant="bars",
                className="loader-icon",
                style={}
            ),
            dmc.ScrollArea([
                graph,
            ])
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
        zIndex=10000,
    ),

]


discover_app = dmc.MantineProvider(
    id=ID_APP_THEME,
    theme={
        "colorScheme": "light",
        "primaryColor": "green",
        "shadows": {
            # other shadows (xs, sm, lg) will be merged from default theme
            "md": "1px 1px 3px rgba(0,0,0,.25)",
            "xl": "5px 5px 3px rgba(0,0,0,.25)",
        },
        "headings": {
            "fontFamily": "Roboto, sans-serif",
            "sizes": {
                "h1": {"fontSize": 20},
            },
        },
    },
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
    Input(ID_URL_LOCATION, 'href'),
)
def display_page(href):
    lat = map_config.DEFAULT_LAT
    lon = map_config.DEFAULT_LON
    query = urlparse(href).query
    query_params: dict = parse_qs(query)
    if query_params:
        lat = query_params["lat"][0]
        lon = query_params["lon"][0]

    return lat, lon


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
    prevent_initial_call=True
)
def map_click(click_lat_lng):
    loc = ""
    if click_lat_lng is not None:
        loc = [f"?lat={click_lat_lng[0]}&lon={click_lat_lng[1]}"]
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
    Output(ID_LOADER, "style", allow_duplicate=True),
    Output(ID_MEASUREMENT_CHART, "style", allow_duplicate=True),
    Input({"role": ALL, "development_id": ALL, "label": ALL}, "n_clicks"),
    State(ID_MARKER_CLICK_STORE, "data"),
    State(ID_CURRENT_CHART_DATA, "data"),
    prevent_initial_call=True,
)
def marker_click(n_clicks, data, chart_data):
    print("click", dash.ctx.triggered_id)
    # determine whether the callback is triggered by a click
    # necessary, because adding markers to the map triggers the callback
    click_sum = safe_reduce(lambda x, y: x + y, n_clicks)
    has_click_triggered = click_sum != data["clicks"]

    if click_sum is not None:
        data["clicks"] = click_sum

    open_drawer = False
    loader_style = {"visibility": "hidden"}
    if has_click_triggered and dash.ctx.triggered_id is not None:
        trigger_id = dash.ctx.triggered_id
        chart_data = dict(role=trigger_id["role"], id=trigger_id["development_id"])
        open_drawer = True
        loader_style = {"visibility": "visible"}

    figure_style = {"visibility": "hidden"}
    return open_drawer, "bottom", data, chart_data, loader_style, figure_style


@app.callback(
    Output(ID_MEASUREMENT_CHART, "figure"),
    Output(ID_MEASUREMENT_CHART, "style", allow_duplicate=True),
    Output(ID_LOADER, "style", allow_duplicate=True),
    Input(ID_CURRENT_CHART_DATA, "data"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def display_chart(data, theme):
    print("display chart: ", data)
    loader_style = {"visibility": "hidden"}
    figure_style = {"visibility": "visible"}
    deployment_id = data["id"]
    match data["role"]:
        case "Env. Sensor": new_figure = create_env_chart(deployment_id, theme)
        case "Pax Counter": new_figure = create_pax_chart(deployment_id, theme)
        case _: return px.line(), figure_style, loader_style
    return new_figure, figure_style, loader_style
