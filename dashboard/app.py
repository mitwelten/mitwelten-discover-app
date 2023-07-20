import dash
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Output, Input, html, dcc
from dash_iconify import DashIconify

from dashboard.components.map_layer_selection import map_selection
from dashboard.components.settings import settings
from dashboard.config import map_config as config
from dashboard.maindash import app


initial_map = config.map_configs[1]
initial_figure = go.Figure(
    go.Scattermapbox(),
    layout_mapbox_style=initial_map.style,
    layout_mapbox_zoom=config.DEFAULT_ZOOM,
    layout_mapbox_layers=[initial_map.layers],
    layout_mapbox_center={'lon': config.DEFAULT_LON, 'lat': config.DEFAULT_LAT},
    layout_margin={'r': 0, 'l': 0, 't': 0, 'b': 0},
)


app_content = [
    html.Div(
        dcc.Graph(id="map_id"),
        id="map-container",
    ),
    dmc.MediaQuery([
            dmc.ActionIcon(
                DashIconify(
                    icon="material-symbols:layers-outline",
                    width=20,
                    color=dmc.theme.DEFAULT_COLORS["green"][9],
                ),
                variant="light",
                size="lg",
                id="bottom-drawer-btn",
                n_clicks=0,
                radius="xl",
            ),
        ],
        largerThan="sm",
        styles={"visibility": "hidden"}
    ),
    dmc.MediaQuery([
        dmc.ActionIcon(
            DashIconify(
                icon="material-symbols:layers-outline",
                width=20,
                color=dmc.theme.DEFAULT_COLORS["green"][9],
            ),
            variant="light",
            size="lg",
            id="map-selector-btn",
            n_clicks=0,
            radius="xl",
        ),
    ],
        smallerThan="sm",
        styles={"visibility": "hidden"}
    ),
    dmc.Card(
        children=[map_selection("on-map")],
        id="map-selector",
        withBorder=True,
        shadow="lg",
        radius="md",
    ),
    dmc.ActionIcon(
        DashIconify(
            icon="material-symbols:menu",
            width=20,
            color=dmc.theme.DEFAULT_COLORS["green"][9],
        ),
        variant="light",
        size="lg",
        id="left-drawer-btn",
        n_clicks=0,
        radius="xl"
    ),
    dmc.Drawer(
        map_selection("on-drawer"),
        id="bottom-drawer",
        zIndex=10000,
    ),
    dmc.Drawer(
        settings(),
        id="left-drawer",
        opened=True,
        size=400,
        padding="md",
        closeOnClickOutside=False,
        withOverlay=False,
        zIndex=10000,
    ),
    html.Div(id="test-id")
]


discover_app = dmc.MantineProvider(
    id="app-theme",
    theme={
        "colorScheme": "dark",
        "primaryColor": "green",
        "shadows": {
            # other shadows (xs, sm, lg) will be merged from default theme
            "md": "1px 1px 3px rgba(0,0,0,.25)",
            "xl": "5px 5px 3px rgba(0,0,0,.25)",
        },
        "headings": {
            "fontFamily": "Roboto, sans-serif",
            "sizes": {
                "h1": {"fontSize": 30},
            },
        },
    },
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        html.Div(
            children=app_content,
            id="app-container",
        ),
    ]
)

app.layout = discover_app


@app.callback(
    Output("map-selector", "style"),
    [
        Input("map-selector-btn", "n_clicks"),
        Input("map-selector", "style"),
    ],
    prevent_initial_call=True,
)
def show_map_selector(_, style):
    if style is not None and style["visibility"] == "visible":
        return {"visibility": "hidden"}
    else:
        return {"visibility": "visible"}


@app.callback(
    Output("bottom-drawer", "opened"),
    Output("bottom-drawer", "position"),
    Input("bottom-drawer-btn", "n_clicks"),
    prevent_initial_call=True,
)
def drawer_demo(n_clicks):
    return True, "bottom"


@app.callback(
    Output("left-drawer", "opened"),
    Output("left-drawer", "position"),
    Input("left-drawer-btn", "n_clicks"),
    prevent_initial_call=True,
)
def drawer_demo(n_clicks):
    return True, "left"
