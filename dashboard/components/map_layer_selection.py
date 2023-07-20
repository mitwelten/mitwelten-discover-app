import dash
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import html, Output, Input, ALL, State, callback

from dashboard.config import map_config as config


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
    Output(component_id="map_id", component_property="figure"),
    [Input(component_id={'role': "minimap-btn", 'index': ALL, 'place': ALL}, component_property='n_clicks'),
     Input(component_id="map_id", component_property="figure")]
)
def minimap_action(_, data):

    new_map = config.map_configs[config.DEFAULT_MAP_INDEX]
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
    new_fig.update_layout(clickmode='event')
    return new_fig


@callback(
    Output("test-id","children"),
    Input("map_id", "clickData"),
)
def mapClick(clickData):
    print(clickData)
    return clickData
