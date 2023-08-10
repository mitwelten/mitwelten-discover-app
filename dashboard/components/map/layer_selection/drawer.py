import dash_mantine_components as dmc
from dash import html

from dashboard.config.map import MAPS, OVERLAYS, MAP_TYPES

# unused import is used to initialize callbacks !
import dashboard.components.map.layer_selection.callbacks


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
