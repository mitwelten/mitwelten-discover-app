import dash_leaflet as dl
from dashboard.config import map_config
from dashboard.config.id_config import *

initial_map = map_config.map_configs[0]
map_figure = dl.Map(
    [
        dl.TileLayer(id=ID_TILE_LAYER_MAP),
        dl.LocateControl(options={"locateOptions": {"enableHighAccuracy": True}}),
        dl.LayerGroup(id=ID_MAP_LAYER_GROUP),
    ],
    zoom=15,
    id=ID_MAP,
    style={
        "width": "100vw",
        "height": "100vh",
        "zIndex": 0,
    },
)
