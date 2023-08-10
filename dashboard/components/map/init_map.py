from urllib.parse import urlparse, parse_qs

import dash_leaflet as dl
from dash import Output, Input

from dashboard.config import map as map_config
from dashboard.config.id import *
from dashboard.config.map import *
from dashboard.config.map import DEFAULT_MAX_ZOOM
from dashboard.maindash import app

initial_map = map_config.MAPS[0]
map_figure = dl.Map(
    [
        dl.Pane(
            dl.TileLayer(
                id=ID_BASE_LAYER_MAP,
                url="",
                attribution="",
                maxZoom=DEFAULT_MAX_ZOOM,
                zIndex=0
            ),
        ),
        dl.FeatureGroup(
            [
                dl.ScaleControl(position="bottomright"),
                dl.LocateControl(
                    options={"locateOptions": {"enableHighAccuracy": True}, "position":"bottomright"},
                ),
            ]
        ),
        dl.LayerGroup(id=ID_MAP_LAYER_GROUP),
        dl.LayerGroup(id=ID_ENV_LAYER_GROUP),
        dl.LayerGroup(id=ID_HIGHLIGHT_LAYER_GROUP),
        dl.LayerGroup(id=ID_NOTES_LAYER_GROUP),
        dl.Pane(
            dl.TileLayer(
                url="",
                attribution="",
                id=ID_OVERLAY_MAP,
                maxZoom=DEFAULT_MAX_ZOOM,
                opacity=0.5,
            ),
        ),
    ],
    doubleClickZoom=False,
    useFlyTo=False,
    zoomControl={"position": "bottomright"},
    zoom=15,
    id=ID_MAP,
    className="id-map",
    style={
        "width": "100vw",
        "height": "100vh",
        "zIndex": 0,
    },
)


@app.callback(
    Output(ID_MAP, 'center', allow_duplicate=True),
    Output(ID_MAP, 'zoom', allow_duplicate=True),
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
        lat = query_params["lat"][0]
        lon = query_params["lon"][0]
        zoom = query_params["zoom"][0]

    return (lat, lon), zoom
