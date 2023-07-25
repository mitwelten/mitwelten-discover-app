import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from dashboard.config.id_config import ID_MINIMAP_LAYER_BUTTON, ID_MINIMAP_LABEL

layer_button = html.Div(
    children=[
        html.Div(
            id=ID_MINIMAP_LAYER_BUTTON,
            children=[
                html.Div(
                    id=ID_MINIMAP_LABEL,
                    children=[
                        DashIconify(icon="bx:layer", width=20, style={'color': "white"}),
                        html.P(
                            "Layers",
                            style={'color': "white", 'fontSize': 13}),
                    ]
                ),
            ]
        ),
        dmc.Image(
            src="./assets/swiss_topo_picture.png",
            alt="map",
            width=96,
            radius=10,
        ),
    ]
)
