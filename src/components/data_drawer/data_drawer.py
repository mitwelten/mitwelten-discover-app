import dash
import dash_mantine_components as dmc
from dash import Output, Input, html, State
from dash.exceptions import PreventUpdate

from src.components.data_drawer.types.audio import create_audio_chart
from src.components.data_drawer.types.env import create_env_chart
from src.components.data_drawer.types.note.detail_view import note_detail_view
from src.components.data_drawer.types.note.form_view import note_form
from src.components.data_drawer.types.pax import create_pax_chart
from src.components.data_drawer.types.pollinator import create_pollinator_chart
from src.components.data_drawer.types.environment_point import create_environment_point_chart
from src.config.app_config import SETTINGS_DRAWER_WIDTH, DATA_SOURCES_WITHOUT_CHART_SUPPORT
from src.config.id_config import *
from src.main import app
from src.model.note import Note
from src.util.util import get_identification_label


chart_drawer = dmc.Drawer(
    opened=False,
    id=ID_CHART_DRAWER,
    zIndex=90000,
    size=SETTINGS_DRAWER_WIDTH,
    closeOnClickOutside=True,
    closeOnEscape=True,
    withOverlay=False,
    overlayOpacity=0,
    className="chart-drawer",
    position="bottom",
    title=dmc.Text(id=ID_DATA_DRAWER_TITLE, weight=500, style={"marginTop": "1em", "marginLeft": "1em"}),
    children=[
        html.Div(id=ID_CHART_CONTAINER, className="chart-container"),
    ],
    # children=[
    #     html.Div(
    #         children=dmc.LoadingOverlay(
    #             html.Div(id=ID_CHART_CONTAINER, className="chart-container"),
    #             loaderProps={"variant": "dots", "color": "mitwelten_pink", "size": "xl"},
    #             style={"height":"100%"},
    #         ),
    #         className="chart-container"
    #     ),
    # ],
)


@app.callback(
    Output(ID_LOGO_CONTAINER, "style"),
    Output(ID_CHART_DRAWER, "styles"),
    # Output("id-search-bar-container", "style"),
    Input(ID_SETTINGS_DRAWER, "opened")
)
def settings_drawer_state(state):
    width_reduced = {"width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}
    full_width = {"width": "100vw"}
    if state:
        return width_reduced, {"drawer": {"left": "400px", "width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}} # width_reduced,
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
    return dash.no_update


@app.callback(
    Output(ID_CHART_CONTAINER, "children"),
    Output(ID_ALERT_INFO, "is_open", allow_duplicate=True),
    Output(ID_ALERT_INFO, "children", allow_duplicate=True),
    Output(ID_DATA_DRAWER_TITLE, "children"),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    State({"role": "Environment Data Point", "label": "Store", "type": "virtual"}, "data"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def update_drawer_content_from_marker_store(selected_marker, environment_data, light_mode):
    if selected_marker is None:
        raise PreventUpdate

    marker_data = selected_marker.get("data")
    node_label = get_identification_label(marker_data)
    drawer_title = f"{selected_marker['type']} - {node_label}"
    match selected_marker["type"]:
        case "Audio Logger":
            drawer_content = create_audio_chart(selected_marker["data"]["id"], light_mode)
        case "Env Sensor":
            drawer_content = create_env_chart(selected_marker["data"]["id"], light_mode)
        case "Pax Counter":
            drawer_content = create_pax_chart(selected_marker["data"]["id"], light_mode)
        case "Pollinator Cam":
            drawer_content = create_pollinator_chart(selected_marker["data"]["id"], light_mode)
        case "Environment Data Point":
            drawer_content = create_environment_point_chart(environment_data["legend"], selected_marker["data"]["id"])
        case "Note":
            drawer_title = ""
            drawer_content = dash.no_update # Nothing to do, content will be updated by the selected note callback
        case _:
            notification = [
                dmc.Title(f"Deployment: {selected_marker['type']}", order=6),
                dmc.Text("No further data available!"),
            ]
            return dash.no_update, True, notification, dash.no_update

    return drawer_content, dash.no_update, dash.no_update, drawer_title


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    prevent_initial_call=True
)
def add_selected_note_into_store(selected_marker, all_notes):
    if selected_marker is None:
        raise PreventUpdate

    if selected_marker["type"] == "Note":
        for note in all_notes["entries"]:
            if note["id"] == selected_marker["data"]["id"]:
                print("update selected note store")
                return dict(data=selected_marker["data"], inEditMode=False, isDirty=False)

        return dict(data=selected_marker["data"], inEditMode=True, isDirty=False)  # new created note

    raise PreventUpdate


@app.callback(
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size"),
    Input(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_TAG_DATA_STORE, "data"),
    prevent_initial_call=True
)
def update_content_from_store(selected_note, all_tags):
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

    is_edit_mode = selected_note.get("inEditMode", False)
    note = Note(selected_note["data"])

    if is_edit_mode:
        return note_form(note, all_tags), 500
    else:
        return note_detail_view(note), 400
