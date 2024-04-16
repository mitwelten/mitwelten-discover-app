from datetime import datetime
import dash_mantine_components as dmc
from dash import ctx, Output, Input, html, State, no_update
from dash.exceptions import PreventUpdate
from src.components.data_drawer.types.wild_cam import create_wild_cam_view
from src.components.data_drawer.types.note.note_view import note_view
from src.model.note import Note

from src.util.user_validation import get_user_from_cookies
from src.components.data_drawer.types.audio import create_audio_chart2
from src.components.button.components.action_button import action_button
from src.components.data_drawer.types.env import create_env_chart
from src.components.data_drawer.types.environment_point import create_environment_point_chart
from src.components.data_drawer.types.pax import create_pax_chart
from src.components.data_drawer.types.pollinator import create_pollinator_chart2
from src.config.app_config import CHART_DRAWER_HEIGHT, SETTINGS_DRAWER_WIDTH, DATA_SOURCES_WITHOUT_CHART_SUPPORT
from src.config.id_config import *
from src.config.app_config import CHART_DRAWER_HEIGHT, PRIMARY_COLOR
from src.main import app
from src.util.util import get_identification_label, local_formatted_date



chart_drawer = dmc.Drawer(
        opened=False,
        id=ID_CHART_DRAWER,
        zIndex=90000,
        size=500,
        closeOnClickOutside=True,
        closeOnEscape=True,
        withOverlay=False,
        overlayOpacity=0,
        className="chart-drawer",
        position="bottom",
        children=[
                dmc.LoadingOverlay(
                    html.Div(id=ID_CHART_CONTAINER, className=""),
                    overlayBlur="0px",
                    overlayColor=None,
                    overlayOpacity=0,
                    zIndex=99999999
                ),
        ],
    )

@app.callback(
    Output(ID_LOGO_CONTAINER, "style"),
    Output(ID_CHART_DRAWER, "styles"),
    # Output("id-search-bar-container", "style"),
    Input(ID_SETTINGS_DRAWER, "opened"),
    State(ID_SETTINGS_DRAWER, "size")
)
def settings_drawer_state(state, size):
    width_reduced = {"width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}
    full_width = {"width": "100vw"}
    if state:
        return width_reduced, {"drawer": {"left": size, "width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}} # width_reduced,
    return full_width, {"drawer": {"left": "0", "width": "100vw"}}#, full_width,


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    prevent_initial_call=True
)
def open_drawer(selected_marker):
    if selected_marker is None:
        raise PreventUpdate

    if selected_marker["type"] not in DATA_SOURCES_WITHOUT_CHART_SUPPORT:
        return True
    return no_update


# TODO: Refactor to a dispatch method
@app.callback(
    Output(ID_CHART_CONTAINER, "children"),
    Output(ID_CHART_DRAWER, "size"),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Output(ID_ALERT_INFO, "is_open", allow_duplicate=True),
    Output(ID_ALERT_INFO, "children", allow_duplicate=True),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    Input(ID_DATE_RANGE_STORE, "data"),
    Input(ID_APP_THEME, "theme"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State({"role": "Environment", "label": "Store", "type": "virtual"}, "data"),
    State("id-test-icon-store", "data"),
    prevent_initial_call=True
)
def update_drawer_content_from_marker_store(selected_marker, date_range, theme, notes, environment_data, test_icons):
    if selected_marker is None:
        raise PreventUpdate

    marker_data    = selected_marker.get("data")
    marker_id      = marker_data.get("id")
    node_label     = get_identification_label(marker_data)
    drawer_title   = f"{selected_marker['type']} - {node_label}"
    drawer_content = html.Div("Somthing went wrong, not device found!")
    drawer_size = CHART_DRAWER_HEIGHT

    match selected_marker["type"]:
        case "Audio Logger":
            drawer_content = create_audio_chart2(marker_data, theme)
        case "Wild Cam":
            drawer_content = create_wild_cam_view(marker_data, theme)
        case "Env Sensor":
            drawer_content = create_env_chart(marker_data, theme)
        case "Pax Counter":
            drawer_content = create_pax_chart(marker_data, date_range, theme)
        case "Pollinator Cam":
            drawer_content = create_pollinator_chart2(marker_data, date_range, theme)
        case "Environment":
            drawer_content = create_environment_point_chart(environment_data["legend"], marker_id, theme)
        case "Note":
            for note in notes["entries"]:
                if note["id"] == marker_id:
                    n = Note(note)
                    file_height = 116 if len(n.files) > 3 else 50 if len(n.files) > 0 else 0
                    drawer_size -= 116 - file_height                    
                    drawer_content = note_view(n, file_height, theme, test_icons)
        case _:
            notification = [
                dmc.Title(f"Deployment: {selected_marker['type']}", order=6),
                dmc.Text("No further data available!"),
            ]
            return no_update, no_update, True, True, notification

    return drawer_content, drawer_size, True, no_update, no_update



@app.callback(
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_EDIT_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def activate_preventing_marker_clicks(selected_note):
    if selected_note["data"] is None:
        return dict(state=False)
    return dict(state=True)

