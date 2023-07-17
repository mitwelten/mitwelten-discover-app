from dash import Dash, html, dcc
import plotly.graph_objects as go
import configuration as config


external_stylesheets = [open("./dashboard/assets/styles.css")]
app = Dash(__name__, external_stylesheets=external_stylesheets)


fig = go.Figure(go.Scattermapbox())

fig.update_layout(
    margin={'r': 0, 'l': 0, 't': 0, 'b': 0},
    mapbox={
        "style": "white-bg",
        "zoom": config.DEFAULT_ZOOM,
        "center": {"lat": config.DEFAULT_LAT, "lon": config.DEFAULT_LON},
        "layers": [config.DEFAULT_MAP_LAYER],
    })


# fig.update_layout(
#     margin={'r': 0, 'l': 0, 't': 0, 'b': 0},
#     #mapbox_bounds={"west": -180, "east": -50, "south": 20, "north": 90},
#     mapbox={
#         'accesstoken': 'pk.eyJ1IjoiYXdpbGQiLCJhIjoiY2xrNmx5cnF6MDA5ZzNrcWs1Y3N2eGFnaCJ9._JBLdiQ7jaxI6ASPqWBbiw',
#         'style': "white-bg",
#         'zoom': 15,
#         'center': dict(lat=config.DEFAULT_LAT,
#                        lon=config.DEFAULT_LON,),
#     },
#     showlegend=False
# )


app.layout = html.Div(
    id="map-container",
    children=[
        dcc.Graph(figure=fig)
    ]
)
