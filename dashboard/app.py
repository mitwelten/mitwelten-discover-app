from functools import partial

from dashboard.components.button.buttons import control_buttons
from dashboard.components.data_drawer.drawer import chart_drawer
from dashboard.components.data_drawer.types.devices.pollinator import *
from dashboard.components.map.init_map import map_figure
from dashboard.components.notes.notes import note_modal
from dashboard.components.settings_drawer.drawer import settings_drawer
from dashboard.config.app import app_theme
from dashboard.config.map import DEFAULT_LAT, DEFAULT_LON
from dashboard.init import init_deployment_data, init_environment_data, init_notes

deployments, data_sources, tags = init_deployment_data()
environments, environment_legend = init_environment_data()
notes = init_notes()

app_content = [

    map_figure,
    chart_drawer(),
    *control_buttons(),
    settings_drawer(deployments, tags, data_sources),
    note_modal(),

    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
    dcc.Store(id=ID_DEPLOYMENT_DATA_STORE, data=deployments),
    dcc.Store(id=ID_NOTES_STORE, data=notes),
    dcc.Store(id=ID_TAG_DATA_STORE, data=tags),
    dcc.Store(id=ID_ENV_DATA_STORE, data=environments),
    dcc.Store(id=ID_DEPLOYMENT_MARKER_STORE, data=data_sources),
    dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(clicks=None)),
    dcc.Store(id=ID_BASE_MAP_STORE, data=dict(), storage_type="local"),
    dcc.Store(id=ID_OVERLAY_MAP_STORE, data=dict(), storage_type="local"),
    dcc.Store(id=ID_CURRENT_CHART_DATA_STORE, data=dict(role=None, id=None, location=None)),
    dcc.Store(id=ID_ENVIRONMENT_LEGEND_STORE, data=environment_legend),
    dcc.Store(id=ID_NEW_NOTE_STORE, data=dict()),

    html.Div(
        html.A(
            "MITWELTEN",
            title="mitwelten.org",
            href="https://mitwelten.org",
            target="_blank",
            className="mitwelten-logo"
        ),
        id=ID_MAP_CONTAINER,
    ),


    dcc.Store(id=ID_FOCUS_ON_MAP_LOCATION, data=dict(lat=DEFAULT_LAT, lon=DEFAULT_LON)),
]


discover_app = dmc.MantineProvider(
    id=ID_APP_THEME,
    theme=app_theme,
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        dmc.NotificationsProvider([
            html.Div(
                children=app_content,
                id=ID_APP_CONTAINER,
            ),
            html.Div(id=ID_NOTIFICATION_CONTAINER),
        ]
        ),
    ]
)

app.layout = discover_app


@app.callback(
    Output(ID_URL_LOCATION, "search"),
    Input(ID_MAP, "click_lat_lng"),
    Input(ID_MAP, "zoom"),
    prevent_initial_call=True
)
def map_click(click_lat_lng, zoom):
    loc = ""
    if click_lat_lng is not None:
        loc = f"?lat={click_lat_lng[0]}&lon={click_lat_lng[1]}&zoom={zoom}"
    return loc


def handle_marker_click(data_source, _):
    trigger = dash.ctx.triggered_id
    return dict(role=data_source, id=trigger["id"], lat=trigger["lat"], lon=trigger["lon"])


for source in data_sources:
    app.callback(
        Output(ID_CURRENT_CHART_DATA_STORE, "data", allow_duplicate=True),
        Input({"role": source, "id": ALL, "label": "Node", "lat": ALL, "lon": ALL}, "n_clicks"),
        prevent_initial_call=True
    )(partial(handle_marker_click, source))




