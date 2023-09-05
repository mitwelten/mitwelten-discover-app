import dash
import dash_mantine_components as dmc
from dash import Output, Input, html, ALL, State

from dashboard.components.data_drawer.types.audio import create_audio_chart
from dashboard.components.data_drawer.types.env import create_env_chart
from dashboard.components.data_drawer.types.note.note import create_note_view
from dashboard.components.data_drawer.types.pax import create_pax_chart
from dashboard.components.data_drawer.types.pollinator import create_pollinator_chart
from dashboard.components.data_drawer.types.environment_point import create_environment_point_chart
from dashboard.components.notifications.notification import NotificationType, create_notification
from dashboard.config.app import SETTINGS_DRAWER_WIDTH, DATA_SOURCES_WITHOUT_CHART_SUPPORT
from dashboard.config.id import *
from dashboard.maindash import app
from util.functions import safe_reduce, ensure_marker_visibility


def chart_drawer():
    return dmc.Drawer(
        opened=False,
        id=ID_CHART_DRAWER,
        zIndex=20000,
        size="50%",
        closeOnClickOutside=False,
        closeOnEscape=False,
        withOverlay=False,
        withCloseButton=True,
        className="chart-drawer",
        children=[
            dmc.LoadingOverlay(
                html.Div(children={}, id=ID_CHART_CONTAINER, className="measurement-chart", style={"margin": "20px"}),
                loaderProps={"variant": "dots", "color": "mitwelten_pink", "size": "xl"},
            )
        ],
    )


@app.callback(
    Output(ID_MAP_CONTAINER, "style"),
    Output(ID_CHART_DRAWER, "styles"),
    Input(ID_SETTINGS_DRAWER, "opened")
)
def settings_drawer_state(state):
    width_reduced = {"width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}
    full_width = {"width": "100vw"}
    if state:
        return width_reduced, {"drawer": {"left": "400px", "width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}}
    return full_width, {"drawer": {"left": "0", "width": "100vw"}}


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "position"),
    Output(ID_MAP, "center", allow_duplicate=True),
    Input(ID_CURRENT_DRAWER_DATA_STORE, "data"),
    State(ID_MAP, "bounds"),
    State(ID_MAP, "viewport"),
    prevent_initial_call=True
)
def open_drawer(data, bounds, viewport):
    map_center = viewport["center"]
    new_center = ensure_marker_visibility(
        map_center,
        bounds,
        dict(lat=data["lat"], lon=data["lon"])
    )
    if data["role"] not in DATA_SOURCES_WITHOUT_CHART_SUPPORT:
        return True, "bottom", new_center
    return dash.no_update, dash.no_update, new_center


@app.callback(
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
    Input(ID_CURRENT_DRAWER_DATA_STORE, "data"),
    State(ID_ENVIRONMENT_LEGEND_STORE, "data"),
    State(ID_NOTES_STORE, "data"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def update_drawer_content_from_store(chart_data, legend, notes, light_mode):
    match chart_data["role"]:
        case "Audio Logger": chart_children = create_audio_chart(chart_data["id"], light_mode)
        case "Env. Sensor": chart_children = create_env_chart(chart_data["id"], light_mode)
        case "Pax Counter": chart_children = create_pax_chart(chart_data["id"], light_mode)
        case "Pollinator Cam": chart_children = create_pollinator_chart(chart_data["id"], light_mode)
        case "Notes": chart_children = create_note_view(notes, chart_data["id"], light_mode)
        case "Environment Data Points": chart_children = create_environment_point_chart(legend, chart_data["id"], light_mode)
        case x: return dash.no_update, create_notification(x, "No further data available!", NotificationType.INFO)
    return chart_children, dash.no_update



