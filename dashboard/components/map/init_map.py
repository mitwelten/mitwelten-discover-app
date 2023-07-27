import dash_leaflet as dl
from dashboard.config import map_config
from dashboard.config.id_config import *

initial_map = map_config.map_configs[0]
map_figure = dl.Map(
    [
        dl.TileLayer(
            id=ID_TILE_LAYER_MAP,
            url=initial_map.source,
            attribution=initial_map.source_attribution,
            maxZoom=20.9,
        ),
        dl.LocateControl(options={"locateOptions": {"enableHighAccuracy": True}}),
        dl.LayerGroup(
            id=ID_MAP_LAYER_GROUP,
        ),
    ],
    center=(map_config.DEFAULT_LAT, map_config.DEFAULT_LON),
    zoom=14,
    id=ID_MAP,
    style={
        "width": "100vw",
        "height": "100vh",
        "zIndex": 0,
    },
)

