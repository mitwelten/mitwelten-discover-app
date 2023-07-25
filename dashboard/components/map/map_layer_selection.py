import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, ALL, callback

from dashboard.config import map_config as config
from dashboard.config.id_config import *


def map_selection(id_prefix):
    return dmc.Container(
        children=[
            dmc.Grid(
                list(map(lambda x: minimap_button(id_prefix, x), config.map_configs)),
                gutter="xl",
                grow=True,
            )
        ],
    )


def minimap_button(id_prefix, map_config):
    return dmc.Col(
        html.Div(
            id={'role': "minimap-btn", 'index': map_config.id, 'place': id_prefix},
            className="minimap-btn",
            children=[
                html.Div(
                    className="minimap-button-container",
                    children=[
                        html.Div(
                            className="map-image",
                            children=[
                                dmc.Image(
                                    src=map_config.image,
                                    alt="map",
                                    width=48,
                                    radius=5,
                                ),
                            ]
                        ),
                        html.P(
                            className="minimap-button-label",
                            children=map_config.title,
                            style={'fontSize': 10}
                        )
                    ]
                )
            ]
        ),
        span=2,
    )


@callback(
    Output("map", "children"),
    [
        Input({'role': "minimap-btn", 'index': ALL, 'place': ALL}, 'n_clicks'),
        Input(ID_MAP_LAYER_GROUP, "id"),
        Input(ID_MAP_LAYER_GROUP, "children")
    ]
)
def minimap_action(_, data_layer_id, data_layer):
    if dash.ctx.triggered_id is not None and type(dash.ctx.triggered_id.index) is int:
        new_map = config.map_configs[dash.ctx.triggered_id.index]
    else:
        return dash.no_update

    return [
        dl.TileLayer(
            url=new_map.source,
            attribution=new_map.source_attribution,
            maxZoom=24.0,
        ),
        dl.LocateControl(options={"locateOptions": {"enableHighAccuracy": True}}),
        dl.LayerGroup(
            id=data_layer_id,
            children=data_layer,
        ),
    ]
