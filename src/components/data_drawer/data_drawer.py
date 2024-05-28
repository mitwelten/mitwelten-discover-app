import dash_mantine_components as dmc
from dash import Output, Input, html, State, no_update
from dash.exceptions import PreventUpdate
from src.components.data_drawer.types.note.note_view import note_view
from src.model.note import Note

from src.components.data_drawer.types.audio import create_audio_chart3
from src.components.data_drawer.types.env import create_env_chart
from src.components.data_drawer.types.environment_point import create_environment_point_chart
from src.components.data_drawer.types.pax import create_pax_chart
from src.components.data_drawer.types.pollinator import create_pollinator_chart2
from src.config.app_config import SETTINGS_DRAWER_WIDTH, DATA_SOURCES_WITHOUT_CHART_SUPPORT
from src.config.id_config import *
from src.config.app_config import CHART_DRAWER_HEIGHT
from src.main import app
from src.util.util import get_drawer_size_by_number_of_files


def create_chart_from_source(selected_marker, date_range, theme, notes, environment_data):
    marker_data    = selected_marker.get("data")
    marker_id      = marker_data.get("id")
    drawer_content = html.Div("Somthing went wrong, not device found!")
    drawer_size    = CHART_DRAWER_HEIGHT

    
    match selected_marker["type"]:
        case "Audio Logger":
            drawer_content = create_audio_chart3(marker_data, date_range, theme)
        #case "Wild Cam":
        #    drawer_content = create_wild_cam_view(marker_data, theme)
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
                    drawer_size = get_drawer_size_by_number_of_files(len(n.files))
                    drawer_content = note_view(n, theme)
    return drawer_content, drawer_size



def chart_drawer(args, device, all_notes, env):
    # initially show chart of deivce, if a node_label is set in the query params
    notes = {}
    notes["entries"] = all_notes
    
    drawer_size = 500
    chart = []
    drawer_state = False
    if device is not None:
        start = args.get("start", None)
        end   = args.get("end", None)

        active_device = {}

        if args.get("node_label") is not None:
            active_device["type"] = device["node"]["type"]
            active_device["data"] = device
        elif args.get("env_id") is not None:
            active_device["type"] = "Environment"
            active_device["data"] = device
        else:
            active_device["type"] = "Note"
            active_device["data"] = device


        chart, drawer_size = create_chart_from_source(
                active_device, 
                {"start": start, "end": end}, 
                {"colorScheme": "light"}, 
                notes, 
                env
                )
        drawer_state = True

    return dmc.Drawer(
        opened=drawer_state,
        id=ID_CHART_DRAWER,
        zIndex=90000,
        size=drawer_size,
        closeOnClickOutside=True,
        closeOnEscape=True,
        withOverlay=False,
        overlayOpacity=0,
        className="chart-drawer",
        position="bottom",
        children=[
                dmc.LoadingOverlay(
                    html.Div(
                        id=ID_CHART_CONTAINER, 
                        className="",
                        children=chart
                        ),
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
    prevent_initial_call=True
)
def update_drawer_content_from_marker_store(selected_marker, date_range, theme, notes, environment_data):
    if selected_marker is None:
        raise PreventUpdate

    if selected_marker["type"] in DATA_SOURCES_WITHOUT_CHART_SUPPORT:
        notification = [
                dmc.Title(f"Deployment: {selected_marker['type']}", order=6),
                dmc.Text("No further data available!"),
            ]
        return no_update, no_update, True, True, notification

    drawer_content, drawer_size = create_chart_from_source(
        selected_marker, 
        date_range, 
        theme, 
        notes, 
        environment_data
        )

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

@app.callback(
        Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
        Input(ID_CHART_DRAWER, "opened"),
        prevent_initial_call=True
        )
def close_drawer(opened):
    if opened:
        return no_update
    return []
