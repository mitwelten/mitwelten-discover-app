import dash_mantine_components as dmc
from dash import html, Output, Input, ALL

from src.main import app
from src.config.id_config import *
from src.config.map_config import MAPS, OVERLAYS, MAP_TYPES

# unused import is used to initialize callbacks !


def minimap_button(id_prefix, map_config, role):
    return html.Div(dmc.Stack(
        children=[
            html.Div(
                dmc.Image(
                    src=map_config.image,
                    alt="map",
                    width=48,
                    height=48,
                    radius=5,
                ),
                className="map-image-selected" if map_config.index == 0 else ""
            ),
            dmc.Text(
                size="xs",
                children=map_config.title,
            )
        ],
        align="center",
        spacing="xs",
    ),
        id={'role': role, 'index': map_config.index, 'place': id_prefix},
    )


def map_menu_drawer(id_prefix):
    return dmc.Container(
        children=[
            dmc.Divider(label="Map", labelPosition="center", size="xs"),
            dmc.Space(h=20),
            dmc.Grid(
                list(map(
                    lambda x: dmc.Col(minimap_button(id_prefix, x, MAP_TYPES[0]), style={"textAlign": "center"}, span=3),
                    MAPS)
                ),
                gutter="sm",
                grow=True,
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Overlay", labelPosition="center", size="xs"),
            dmc.Space(h=20),
            dmc.Grid(
                list(map(
                    lambda x: dmc.Col(minimap_button(id_prefix, x, MAP_TYPES[1]), style={"textAlign": "center"}, span=3),
                    OVERLAYS)
                ),
                gutter="sm",
                grow=True,
            ),
        ],
    )


@app.callback(
    Output(ID_MAP_LAYER_BOTTOM_DRAWER, "opened", allow_duplicate=True),
    Input(ID_BOTTOM_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_bottom_drawer(_):
    return True


@app.callback(
    Output(ID_MAP_LAYER_BOTTOM_DRAWER, "opened", allow_duplicate=True),
    Input(ID_MAP, "clickData"),
    Input({'role': ALL, 'index': ALL, 'place': "drawer"}, 'n_clicks'),
    prevent_initial_call=True,
)
def close_bottom_drawer(_1, _2):
    return False
