import json

import dash_leaflet as dl
import dash_mantine_components as dmc
import requests
from dash import Output, Input, html, dcc, dash, State
from dash_iconify import DashIconify
from urllib.parse import urlparse, parse_qs
from functools import reduce

from dashboard.components.map.map_layer_selection import map_selection
from dashboard.components.left_drawer.settings import settings
from dashboard.config import api_config as api
from dashboard.config import map_config as config
from dashboard.config.id_config import *
from dashboard.maindash import app
from dashboard.model.deployment import Deployment


all_deployments = [Deployment(d) for d in requests.get(api.URL_DEPLOYMENTS).json()]

all_types = set(map(lambda d: d.node_type, all_deployments))

all_tags = map(lambda d: d.tags, all_deployments)
all_tags = sorted(set(reduce(list.__add__, all_tags)))
json_tags = json.dumps(all_tags)

deployment_dict = {}
for type in all_types:
    deployment_dict[type] = [d.to_json() for d in all_deployments if type.lower().strip() in d.node_type.lower()]

initial_map = config.map_configs[0]
map_figure = dl.Map(
    [
        dl.TileLayer(
            id=ID_TILE_LAYER_MAP,
            url=initial_map.source,
            attribution=initial_map.source_attribution,
            maxZoom=20.9,
        ),
        dl.LocateControl(options={"locateOptions": {"enableHighAccuracy": True}}),
        dl.LayerGroup(id=ID_MAP_LAYER_GROUP),
    ],
    center=(config.DEFAULT_LAT, config.DEFAULT_LON),
    zoom=14,
    id=ID_MAP,
    style={
        "width": "100vw",
        "height": "100vh",
        "zIndex": 0,
    },
)

app_content = [
    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
    dcc.Store(id=ID_DEPLOYMENT_DATA_STORE, data=deployment_dict),
    dcc.Store(id=ID_TAG_DATA_STORE, data=json_tags),
    dcc.Store(id=ID_POPUP_STATE_STORE, data={'clicks': 0}),
    map_figure,
    dmc.MediaQuery([
            dmc.ActionIcon(
                DashIconify(
                    icon="material-symbols:layers-outline",
                    width=20,
                    color=dmc.theme.DEFAULT_COLORS["green"][9],
                ),
                variant="light",
                size="lg",
                id=ID_BOTTOM_DRAWER_BUTTON,
                n_clicks=0,
                radius="xl",
            ),
        ],
        largerThan="sm",
        styles={"visibility": "hidden"}
    ),
    dmc.MediaQuery([
        dmc.ActionIcon(
            DashIconify(
                icon="material-symbols:layers-outline",
                width=20,
                color=dmc.theme.DEFAULT_COLORS["green"][9],
            ),
            variant="light",
            size="lg",
            id=ID_MAP_SELECTOR_BUTTON,
            n_clicks=0,
            radius="xl",
        ),
    ],
        smallerThan="sm",
        styles={"visibility": "hidden"}
    ),
    dmc.Card(
        children=[map_selection("on-map")],
        id=ID_MAP_SELECTION_POPUP,
        withBorder=True,
        shadow="lg",
        radius="md",
        styles={"visibility": "hidden"}
    ),
    dmc.ActionIcon(
        DashIconify(
            icon="material-symbols:menu",
            width=20,
            color=dmc.theme.DEFAULT_COLORS["green"][9],
        ),
        variant="light",
        size="lg",
        id=ID_OPEN_LEFT_DRAWER_BUTTON,
        n_clicks=0,
        radius="xl"
    ),
    dmc.Drawer(
        map_selection("on-drawer"),
        id=ID_BOTTOM_DRAWER,
        zIndex=10000,
    ),
    dmc.Drawer(
        settings(deployment_dict, all_tags),
        id=ID_LEFT_DRAWER,
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
        "colorScheme": "dark",
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
    lat = config.DEFAULT_LAT
    lon = config.DEFAULT_LON
    query = urlparse(href).query
    r = parse_qs(query)
    if r is not {}:
        lat = r["lat"][0]
        lon = r["lon"][0]

    return (lat, lon)


@app.callback(
    [
        Output(ID_URL_LOCATION, "search"),
        Output(ID_MAP_SELECTION_POPUP, "style"),
        Output(ID_POPUP_STATE_STORE, "data"),
    ],
    [
        Input(ID_MAP_SELECTOR_BUTTON, "n_clicks"),
        Input(ID_MAP, "click_lat_lng"),
        State(ID_POPUP_STATE_STORE, "data"),
    ],
    prevent_initial_callback=True
)
def map_click(n_clicks, click_lat_lng, data):
    popup_style = {"visibility": "hidden"}
    data = data or {'clicks': None}
    if n_clicks is not None:
        if n_clicks != data['clicks']:
            data = {'clicks': n_clicks}
            popup_style = {"visibility": "visible"}
            print("button pressed")

    loc = ""
    if click_lat_lng is not None:
        loc = [f"?lat={click_lat_lng[0]}&lon={click_lat_lng[1]}"]
    return loc, popup_style, data


@app.callback(
    Output(ID_BOTTOM_DRAWER, "opened"),
    Output(ID_BOTTOM_DRAWER, "position"),
    Input(ID_BOTTOM_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def drawer_demo(n_clicks):
    return True, "bottom"


@app.callback(
    Output(ID_LEFT_DRAWER, "opened"),
    Output(ID_LEFT_DRAWER, "position"),
    Input(ID_OPEN_LEFT_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def drawer_demo(n_clicks):
    return True, "left"
