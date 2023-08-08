import dash_leaflet as dl
from dashboard.config import map_config
from dashboard.config.id_config import *
from dashboard.config.map_config import DEFAULT_MAX_ZOOM

initial_map = map_config.MAPS[0]
map_figure = dl.Map(
    [
        dl.Pane(
            dl.TileLayer(
                id=ID_BASE_LAYER_MAP,
                url="",
                attribution="",
                # url=initial_map.source,
                # attribution=initial_map.source_attribution,
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
        dl.LayerGroup(
            id=ID_MAP_LAYER_GROUP,
        ),

        dl.LayerGroup(
            id=ID_ENV_LAYER_GROUP,
        ),
        dl.LayerGroup(
            id=ID_HIGHLIGHT_LAYER_GROUP,
        ),
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
    zoomControl={"position": "bottomright"},
    zoom=15,
    id=ID_MAP,
    style={
        "width": "100vw",
        "height": "100vh",
        "zIndex": 0,
    },
)
