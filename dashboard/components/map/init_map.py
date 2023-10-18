from urllib.parse import urlparse, parse_qs

import dash_leaflet as dl
from dash import Output, Input, State

from dashboard.maindash import app
from dashboard.config import map_config as map_config
from dashboard.config.id_config import *
from dashboard.config.map_config import DEFAULT_MAX_ZOOM, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ZOOM
from dashboard.components.map.layer_selection import callbacks

# import marker callbacks
from dashboard.components.map import markers

url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
initial_map = map_config.MAPS[1]
map_figure = dl.Map([
    dl.TileLayer(
        id=ID_BASE_LAYER_MAP,
        url="",
        attribution="",
        maxZoom=DEFAULT_MAX_ZOOM,
    ),

    dl.TileLayer(
        url="",
        attribution="",
        id=ID_OVERLAY_MAP,
        maxZoom=DEFAULT_MAX_ZOOM,
        opacity=0.5,
    ),

    dl.ScaleControl(position="bottomright"),
    dl.LocateControl(locateOptions={'enableHighAccuracy': True}, position="bottomright"),
    dl.LayerGroup(id=ID_MAP_LAYER_GROUP),
    dl.LayerGroup(id=ID_ENV_LAYER_GROUP),
    dl.LayerGroup(id=ID_HIGHLIGHT_LAYER_GROUP),
    dl.LayerGroup(id=ID_NOTES_LAYER_GROUP),

    ],
    id=ID_MAP,
    viewport=dict(center=[47.5339807306196, 7.6169566067567], zoom=10, transition="flyTo"),
    center=[47.5339807306196, 7.6169566067567],
    zoom=10,
    doubleClickZoom=False,
    className="id-map",
    style={
        "width": "100vw",
        "height": "100vh",
        "zIndex": 0,
    }
)

@app.callback(
    Output(ID_MAP, "viewport", allow_duplicate=True),
    Input(ID_URL_LOCATION, 'href'),
    prevent_initial_call=True
)
def display_page(href):
    lat = DEFAULT_LAT
    lon = DEFAULT_LON
    zoom = DEFAULT_ZOOM
    query = urlparse(href).query
    query_params: dict = parse_qs(query)
    if query_params:
        lat = float(query_params["lat"][0])
        lon = float(query_params["lon"][0])
        zoom = float(query_params["zoom"][0])

    return dict(center=[lat, lon], zoom=zoom, transition="flyTo")
