from dash.exceptions import PreventUpdate
import dash_leaflet as dl
from dash_extensions.javascript import assign
from pprint import pprint
from src.model.base import BaseDeployment
from src.model.url_parameter import UrlParameter
from src.main import app
from dash import Input, Output, State, dcc

from src.model.deployment import Deployment
from src.model.environment import Environment
from src.model.note import Note
from src.config import map_config as map_config
from src.config.id_config import *
from src.config.map_config import DEFAULT_LAT, DEFAULT_LON, DEFAULT_MAX_ZOOM

# import marker callbacks
import src.components.map.layer_selection.callbacks
import src.components.map.markers
from src.components.settings_drawer.components.marker_popup import environment_popup, device_popup, note_popup
import dash_mantine_components as dmc

initial_map = map_config.MAPS[1]

def map_figure(params: UrlParameter, active_depl: BaseDeployment|None): 

    initial_center = [params.lat, params.lon]
    base_layers = []
    for map in map_config.MAPS:
        base_layers.append(
                dl.BaseLayer(
                    id=f"layer-{map.index}",
                    name=map.title,
                    children=dl.TileLayer(
                        url=map.source, 
                        attribution=map.source_attribution, 
                        maxZoom=DEFAULT_MAX_ZOOM)
                    )
                )

    overlay_layers = []
    for map in map_config.OVERLAYS:
        overlay_layers.append(
                dl.Overlay(
                    name=map.title,
                    children=dl.TileLayer(
                        url=map.source, 
                        attribution=map.source_attribution, 
                        maxZoom=DEFAULT_MAX_ZOOM)
                    )
                )

    return dl.Map([


    dcc.Store(
        id="id-active-depl-store", 
        data=dict(
            args=params.to_dict(), 
            active_depl=active_depl.to_dict() if active_depl is not None else None
            )
        ),

    dl.LayersControl(
        id="id-layer-control",
        children=[
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
            dl.Overlay(
                id="notes-overlay", 
                name="Notes", 
                checked=True,
                children=dl.LayerGroup(id=ID_NOTES_LAYER_GROUP)
                ),
            dl.Overlay(
                id="env-overlay", 
                name="Env", 
                checked=True,
                children=dl.LayerGroup(id=ID_ENV_LAYER_GROUP)
                ),

            dl.Overlay(
                id="deployment-overlay", 
                name="Deployments", 
                checked=True,
                children= dl.LayerGroup(id=ID_DEPLOYMENT_LAYER_GROUP),
                ),
            ]
        ),
    dl.ScaleControl(position="bottomright"),
    dl.LocateControl(locateOptions={'enableHighAccuracy': True}, position="bottomright"),
    dl.LayerGroup(id=ID_HIGHLIGHT_LAYER_GROUP),
    dl.LayerGroup(id=ID_INIT_POPUP_LAYER),
    ],
    id=ID_MAP,
    center=initial_center,
    zoom=int(float(params.zoom)),
    maxZoom=DEFAULT_MAX_ZOOM,
    zoomSnap=0,
    doubleClickZoom=False,
    className="id-map",
    style={
        "width": "100vw",
        "height": "100vh",
        "zIndex": 0,
    },
)

@app.callback(
        Output(ID_INIT_POPUP_LAYER, "children"),
        Input(ID_TIMEZONE_STORE, "data"),
        State("id-active-depl-store", "data"),
)
def init_popup_time(timezone, data):
    active_depl = data["active_depl"]
    args = data["args"]

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
            children=popup_fn(active_depl, timezone.get("tz")),
            closeButton=False,
            autoPan=False,
            autoClose=False,
            position=[active_depl.lat, active_depl.lon],
        )
    return init_popup
