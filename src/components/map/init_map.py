import dash_leaflet as dl
from dash_extensions.javascript import assign

from src.config import map_config as map_config
from src.config.id_config import *
from src.config.map_config import DEFAULT_MAX_ZOOM

# import marker callbacks
import src.components.map.layer_selection.callbacks
import src.components.map.markers

initial_map = map_config.MAPS[1]

def map_figure(args, active_depl): 
    if active_depl is not None:
        print(active_depl)
        print(active_depl)

    return dl.Map([
    dl.TileLayer(
        id=ID_BASE_LAYER_MAP,
        url=initial_map.source,
        attribution="",
        maxZoom=DEFAULT_MAX_ZOOM,
        maxNativeZoom=19,
    ),

    dl.TileLayer(
        url="",
        attribution="",
        id=ID_OVERLAY_MAP,
        maxZoom=DEFAULT_MAX_ZOOM,
        opacity=0.5,
        maxNativeZoom=19,
    ),

    dl.ScaleControl(position="bottomright"),
    dl.LocateControl(locateOptions={'enableHighAccuracy': True}, position="bottomright"),
    dl.LayerGroup(id=ID_MAP_LAYER_GROUP),
    dl.LayerGroup(id=ID_ENV_LAYER_GROUP),
    dl.LayerGroup(id=ID_HIGHLIGHT_LAYER_GROUP),
    dl.LayerGroup(id=ID_NOTES_LAYER_GROUP),

    ],
    id=ID_MAP,
    #viewport=dict(center=[47.5339807306196, 7.6169566067567], zoom=10, transition="flyTo"),
    center=[args.get("lat", 47.5339807306196), args.get("lon", 7.6169566067567)],
    zoom=args.get("zoom", 12),
    maxZoom=DEFAULT_MAX_ZOOM,
    doubleClickZoom=False,
    className="id-map",
    style={
        "width": "100vw",
        "height": "100vh",
        "zIndex": 0,
    },
)
