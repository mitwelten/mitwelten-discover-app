import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, ALL, State
from dashboard.maindash import app

from dashboard.config import map_config as config
from dashboard.config.id_config import *


def map_selection(id_prefix):
    return dmc.Container(
        children=[
            dmc.Grid(
                list(map(lambda x: minimap_button(id_prefix, x), config.map_configs)),
                gutter="xl",
                grow=True,
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Overlays", labelPosition="center", size="sm"),
            dmc.Space(h=20),
            dmc.Grid(
                list(map(lambda x: minimap_button(f"test-{id_prefix}", x), config.map_configs[1:-1])),
                gutter="xl",
                grow=True,
            ),
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
        style={"textAlign": "center"},
        span=3,
    )


@app.callback(
    Output(ID_MAP, "children"),
    Input({'role': "minimap-btn", 'index': ALL, 'place': ALL}, 'n_clicks'),
    State(ID_MAP_LAYER_GROUP, "children"),
)
def minimap_action(_, data_layer):
    if dash.ctx.triggered_id is not None and type(dash.ctx.triggered_id.index) is int:
        new_map = config.map_configs[dash.ctx.triggered_id.index]
    else:
        return dash.no_update

    return [
        dl.TileLayer(
            url=new_map.source,
            attribution=new_map.source_attribution,
            maxZoom=20.9,
        ),
        dl.LocateControl(options={"locateOptions": {"enableHighAccuracy": True}}),
        dl.LayerGroup(
            id=ID_MAP_LAYER_GROUP,
            children=data_layer,
        ),
    ]
