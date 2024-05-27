import dash_leaflet as dl
from dash_extensions.javascript import assign

from src.model.deployment import Deployment
from src.model.environment import Environment
from src.model.note import Note
from src.config import map_config as map_config
from src.config.id_config import *
from src.config.map_config import DEFAULT_MAX_ZOOM

# import marker callbacks
import src.components.map.layer_selection.callbacks
import src.components.map.markers
from src.components.settings_drawer.components.marker_popup import environment_popup, device_popup, note_popup

initial_map = map_config.MAPS[1]

def map_figure(args, active_depl): 
    init_center = [args.get("lat"), args.get("lon")]
    init_popup = None

    if active_depl is not None:

        if args.get("node_label") is not None:
            active_depl = Deployment(active_depl)
            popup_fn = device_popup
        elif args.get("env_id") is not None:
            popup_fn = environment_popup
            active_depl = Environment(active_depl)
        else:
            popup_fn = note_popup
            active_depl = Note(active_depl)


        init_popup = dl.Popup(
            children=popup_fn(active_depl),
            closeButton=False,
            id="init-popup",
            autoPan=False,
            autoClose=False,
            position=[active_depl.lat, active_depl.lon],
        )

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
    dl.LayerGroup(id="init-popup-layer", children=init_popup),
    ],
    id=ID_MAP,
    center=init_center,
    zoom=args.get("zoom"),
    maxZoom=DEFAULT_MAX_ZOOM,
    doubleClickZoom=False,
    className="id-map",
    style={
        "width": "100vw",
        "height": "100vh",
        "zIndex": 0,
    },
)


