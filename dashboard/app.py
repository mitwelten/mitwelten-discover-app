from urllib.parse import urlparse, parse_qs

import dash
import dash_mantine_components as dmc
import plotly.express as px
from dash import Output, Input, html, dcc, State, ALL
from dash_iconify import DashIconify

from dashboard.components.chart_modal.chart import create_env_chart, create_pax_chart
from dashboard.components.left_drawer.settings import settings_content
from dashboard.components.map.init_map import map_figure
from dashboard.components.map.map_layer_selection import map_selection
from dashboard.config import map_config
from dashboard.config.id_config import *
from dashboard.init import init_app_data
from dashboard.maindash import app
from util.functions import safe_reduce

deployments, colors,  tags = init_app_data()

fig = px.line()

graph = dmc.Container(
    dcc.Graph(
        id=ID_MEASUREMENT_CHART,
        figure=fig,
        config={"displayModeBar": False},
        style={"height": "inherit", "width": "inherit"}
    ),
)

app_content = [
    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
    dcc.Store(id=ID_DEPLOYMENT_DATA_STORE, data=deployments),
    dcc.Store(id=ID_TAG_DATA_STORE, data=tags),
    dcc.Store(id=ID_DEPLOYMENT_COLOR_STORE, data=colors),
    dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(clicks=None)),
    dmc.Loader(
        id=ID_LOADER,
        color="blue",
        size="lg",
        variant="bars",
        className="loader-icon",
    ),
    map_figure,
    dmc.MediaQuery([
            dmc.ActionIcon(
                DashIconify(
                    icon="material-symbols:layers-outline",
                    width=20,
                    color=dmc.theme.DEFAULT_COLORS["green"][9],
                ),
                variant="light",
                size="lg",
                id=ID_BOTTOM_DRAWER_BUTTON,
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
            id=ID_MAP_SELECTOR_BUTTON,
            n_clicks=0,
            radius="xl",
        ),
    ],
        smallerThan="sm",
        styles={"visibility": "hidden"}
    ),
    dmc.Card(
        children=[map_selection("on-map")],
        id=ID_MAP_SELECTION_POPUP,
        withBorder=True,
        shadow="lg",
        radius="md",
        style={"visibility": "hidden"}
    ),
    dmc.ActionIcon(
        DashIconify(
            icon="material-symbols:menu",
            width=20,
            color=dmc.theme.DEFAULT_COLORS["green"][9],
        ),
        variant="light",
        size="lg",
        id=ID_OPEN_LEFT_DRAWER_BUTTON,
        n_clicks=0,
        radius="xl"
    ),
    dmc.Drawer(
        map_selection("on-drawer"),
        id=ID_BOTTOM_DRAWER,
        zIndex=10000,
    ),
    dmc.Modal(
        title="Measurement Chart",
        opened=False,
        id=ID_CHART_DRAWER,
        zIndex=20000,
        size="80%",
        children=[
            dmc.ScrollArea([
                graph
            ],
            )
        ]
    ),
    dmc.Drawer(
        id=ID_LEFT_DRAWER,
        children=settings_content(deployments, tags, colors),
        opened=True,
        size=400,
        padding="md",
        closeOnClickOutside=False,
        closeOnEscape=False,
        withOverlay=False,
        zIndex=10000,
    ),
]


discover_app = dmc.MantineProvider(
    id=ID_APP_THEME,
    theme={
        "colorScheme": "light",
        "primaryColor": "green",
        "shadows": {
            # other shadows (xs, sm, lg) will be merged from default theme
            "md": "1px 1px 3px rgba(0,0,0,.25)",
            "xl": "5px 5px 3px rgba(0,0,0,.25)",
        },
        "headings": {
            "fontFamily": "Roboto, sans-serif",
            "sizes": {
                "h1": {"fontSize": 20},
            },
        },
    },
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        html.Div(
            children=app_content,
            id=ID_APP_CONTAINER,
        ),
    ]
)

app.layout = discover_app


@app.callback(
    Output(ID_MAP, 'center'),
    Input(ID_URL_LOCATION, 'href'),
)
def display_page(href):
    lat = map_config.DEFAULT_LAT
    lon = map_config.DEFAULT_LON
    query = urlparse(href).query
    query_params: dict = parse_qs(query)
    if query_params:
        lat = query_params["lat"][0]
        lon = query_params["lon"][0]

    return lat, lon


@app.callback(
    Output(ID_MAP_SELECTION_POPUP, "style", allow_duplicate=True),
    Input(ID_MAP_SELECTOR_BUTTON, "n_clicks"),
    State(ID_MAP_SELECTION_POPUP, "style"),
    prevent_initial_call=True
)
def toggle_map_selection_popup(_, style):
    if style is None or style["visibility"] == "visible":
        return {"visibility": "hidden"}

    return {"visibility": "visible"}


@app.callback(
    Output(ID_URL_LOCATION, "search"),
    Output(ID_MAP_SELECTION_POPUP, "style", allow_duplicate=True),
    Input(ID_MAP, "click_lat_lng"),
    prevent_initial_call=True
)
def map_click(click_lat_lng):
    loc = ""
    if click_lat_lng is not None:
        loc = [f"?lat={click_lat_lng[0]}&lon={click_lat_lng[1]}"]
    return loc, {"visibility": "hidden"}


@app.callback(
    Output(ID_BOTTOM_DRAWER, "opened"),
    Output(ID_BOTTOM_DRAWER, "position"),
    Input(ID_BOTTOM_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_bottom_drawer(_):
    return True, "bottom"


@app.callback(
    Output(ID_LEFT_DRAWER, "opened"),
    Output(ID_LEFT_DRAWER, "position"),
    Input(ID_OPEN_LEFT_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_left_drawer(_):
    return True, "left"


@app.callback(
    Output(ID_MEASUREMENT_CHART, "figure"),
    Output(ID_CHART_DRAWER, "opened"),
    Output(ID_MARKER_CLICK_STORE, "data"),
    Input({"role": ALL, "id": ALL, "label": ALL}, "n_clicks"),
    Input(ID_MARKER_CLICK_STORE, "data"),
    running=[
        (
                Output(ID_LOADER, "style"),
                {"visibility": "visible"},
                {"visibility": "hidden"},
        ),
    ],
    prevent_initial_call=True,
)
def marker_click(n_clicks, data):
    click_sum = safe_reduce(lambda x, y: x + y, n_clicks)
    print(dash.ctx.triggered_id)

    has_click_triggered = click_sum != data["clicks"]

    if click_sum is not None:
        data["clicks"] = click_sum

    if has_click_triggered and dash.ctx.triggered_id is not None:
        trigger_id = dash.ctx.triggered_id["id"]
        match dash.ctx.triggered_id["role"]:
            case "Env. Sensor": new_figure = create_env_chart(trigger_id)
            case "Pax Counter": new_figure = create_pax_chart(trigger_id)
            # case "Wild Cam": new_figure = create_wild_cam_chart(trigger_id)
            case _: return dash.no_update

        return new_figure, True, data
    return px.line(), False, data
