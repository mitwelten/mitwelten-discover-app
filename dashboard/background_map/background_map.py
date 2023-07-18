import dash
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import html, Output, Input, ALL
from dash_iconify import DashIconify

from dashboard.background_map import map_config as config
from dashboard.maindash import app


def map_selector():
    chooser = dmc.HoverCard(
        shadow="md",
        children=[
            dmc.HoverCardTarget(
                html.Div(
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
                ),
            ),
            dmc.HoverCardDropdown(
                [dmc.Group(list(map(lambda x: minimap_button(x), config.map_configs)))]
            ),
        ],
    )
    return chooser


def minimap_button(map_config):
    return html.Div(
        id={'role': "minimap-btn", 'index': map_config.id},
        children=[
            html.Div(
                id="minimap-button-container",
                children=[
                    html.Div(
                        id="map-image",
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
                        id="minimap-button-label",
                        children=map_config.title,
                        style={'fontSize': 10}
                    )
                ]
            )
        ]
    )


@app.callback(
    Output(component_id="map_id", component_property="figure"),
    [Input(component_id={'role': "minimap-btn", 'index': ALL}, component_property='n_clicks'),
     Input(component_id="map_id", component_property="figure")]
)
def minimap_action(_, data):

    new_map = config.map_configs[0]
    prev_zoom = config.DEFAULT_ZOOM
    center = {'lon': config.DEFAULT_LON, 'lat': config.DEFAULT_LAT}

    if data is not None:
        mapbox = data["layout"]["mapbox"]
        prev_zoom = mapbox["zoom"]
        center = mapbox["center"]

    if dash.ctx.triggered_id is not None:
        new_map = config.map_configs[dash.ctx.triggered_id.index]

    new_fig = go.Figure(
        go.Scattermapbox(),
        layout_mapbox_style=new_map.style,
        layout_mapbox_zoom=prev_zoom,
        layout_mapbox_layers=[new_map.layers],
        layout_mapbox_center=center,
        layout_margin={'r': 0, 'l': 0, 't': 0, 'b': 0},
    )
    return new_fig

