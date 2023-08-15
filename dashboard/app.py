import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import Output, Input, html, dcc, State

from dashboard.components.data_drawer.types.note import create_note_form
from dashboard.components.notes.notes import note_modal
from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.components.button.buttons import control_buttons
from dashboard.components.data_drawer.drawer import chart_drawer
from dashboard.components.map.init_map import map_figure
from dashboard.components.settings_drawer.drawer import settings_drawer
from dashboard.config.app import app_theme
from dashboard.init import init_deployment_data, init_environment_data, init_notes
from dashboard.maindash import app
from dashboard.util.user_validation import get_user_from_cookies

deployments, deployment_markers, tags = init_deployment_data()
environments, environment_legend = init_environment_data()
notes = init_notes()

app_content = [
    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
    dcc.Store(id=ID_DEPLOYMENT_DATA_STORE, data=deployments),
    dcc.Store(id=ID_NOTES_STORE, data=notes),
    dcc.Store(id=ID_TAG_DATA_STORE, data=tags),
    dcc.Store(id=ID_ENV_DATA_STORE, data=environments),
    dcc.Store(id=ID_DEPLOYMENT_MARKER_STORE, data=deployment_markers),
    dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(clicks=None)),
    dcc.Store(id=ID_BASE_MAP_STORE, data=dict(), storage_type="local"),
    dcc.Store(id=ID_OVERLAY_MAP_STORE, data=dict(), storage_type="local"),
    dcc.Store(id=ID_CURRENT_CHART_DATA_STORE, data=dict(role=None, id=None, lat=None, lon=None)),
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
    map_figure,
    *control_buttons(),
    chart_drawer(),
    settings_drawer(deployments, tags, deployment_markers),
    note_modal()
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






