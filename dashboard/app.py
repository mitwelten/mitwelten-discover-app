from dash import html, dcc

from dashboard.background_map.background_map import map_selector
from dashboard.maindash import app

app.layout = html.Div(
    id="map-container",
    children=[
        html.Div(children=[
            dcc.Graph(id="map_id"),
        ]),
        html.Div(
            id="map-selector-container",
            children=[map_selector()]
        ),
    ]
)
