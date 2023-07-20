import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

layer_button = html.Div(
    children=[
        html.Div(
            id="minimap-layer-button",
            children=[
                html.Div(
                    id="minimap-label",
                    children=[
                        DashIconify(icon="bx:layer", width=20, style={'color': "white"}),
                        html.P(
                            "Ebenen",
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
