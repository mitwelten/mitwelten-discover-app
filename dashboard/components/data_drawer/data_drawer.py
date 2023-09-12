import dash
import dash_mantine_components as dmc
from dash import Output, Input, html, ALL, State
from dash.exceptions import PreventUpdate

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
        zIndex=90000,
        size="50%",
        closeOnClickOutside=True,
        closeOnEscape=True,
        withOverlay=True,
        overlayOpacity=0,
        withCloseButton=True,
        className="chart-drawer",
        position="bottom",
        styles={"header": {"margin": 0}},
        # children=[
        #     html.Div(id=ID_CHART_CONTAINER, className="chart-container", style={"margin": "20px"}),
        # ],
        children=[
            html.Div(
                children=dmc.LoadingOverlay(
                    html.Div(id=ID_CHART_CONTAINER, className="chart-container"),
                    loaderProps={"variant": "dots", "color": "mitwelten_pink", "size": "xl"},
                    style={"height":"100%"},
                ),
                className="chart-container"
            ),
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
    Output(ID_MAP, "center", allow_duplicate=True),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    State(ID_MAP, "bounds"),
    State(ID_MAP, "viewport"),
    prevent_initial_call=True
)
def open_drawer(selected_marker, bounds, viewport):

    if selected_marker is None:
        raise PreventUpdate

    location = selected_marker["data"]["location"]
    map_center = viewport["center"]
    new_center = ensure_marker_visibility(
        map_center,
        bounds,
        dict(lat=location["lat"], lon=location["lon"])
    )
    if selected_marker["type"] not in DATA_SOURCES_WITHOUT_CHART_SUPPORT:
        return True, new_center
    return dash.no_update, new_center


@app.callback(
    Output(ID_CHART_CONTAINER, "children"),
    Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    State({"role": "Environment Data Points", "label": "Store", "type": "virtual"}, "data"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def update_drawer_content_from_store(selected_marker, environment_data, light_mode):
    if selected_marker is None:
        raise PreventUpdate

    match selected_marker["type"]:
        case "Audio Logger":
            drawer_content = create_audio_chart(selected_marker["data"]["id"], light_mode)
        case "Env. Sensor":
            drawer_content = create_env_chart(selected_marker["data"]["id"], light_mode)
        case "Pax Counter":
            drawer_content = create_pax_chart(selected_marker["data"]["id"], light_mode)
        case "Pollinator Cam":
            drawer_content = create_pollinator_chart(selected_marker["data"]["id"], light_mode)
        case "Environment Data Points":
            drawer_content = create_environment_point_chart(environment_data["legend"], selected_marker["data"]["id"])
        case "Notes": drawer_content = create_note_view()
        case x:
            return dash.no_update, create_notification(x, "No further data available!", NotificationType.INFO)

    return drawer_content, dash.no_update


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    State(ID_NEW_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def add_selected_note_into_store(selected_marker, new_note):
    print("sync marker and note store")
    if selected_marker is None:
        raise PreventUpdate

    if selected_marker["type"] == "Notes":
        if new_note is not None:
            return dict(data=selected_marker["data"], inEditMode=True, movedTo=[new_note["location"]["lat"], new_note["location"]["lon"]])

        return dict(data=selected_marker["data"], inEditMode=False, movedTo=None)
    raise PreventUpdate
