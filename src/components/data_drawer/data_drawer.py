import dash_mantine_components as dmc
from dash_mantine_components import DEFAULT_THEME
from dash import Output, Input, html, State, no_update
from dash.exceptions import PreventUpdate
from pprint import pprint
import dash_core_components as dcc
from src.model.environment import Environment
from src.model.deployment import Deployment
from src.components.notification.notification import NotificationType, notification
from src.components.data_drawer.types.note.note_view import note_view
from src.model.note import Note

from src.config.map_config import get_source_props
from src.components.data_drawer.types.audio import create_audio_chart
from src.components.data_drawer.types.env import create_env_chart
from src.components.data_drawer.types.environment_point import create_environment_point_chart
from src.components.data_drawer.types.pax import create_pax_chart
from src.components.data_drawer.types.pollinator import create_pollinator_chart
from src.config.app_config import BACKGROUND_COLOR, CHART_DRAWER_HEIGHT, SETTINGS_DRAWER_WIDTH, DATA_SOURCES_WITHOUT_CHART_SUPPORT
from src.config.id_config import *
from src.main import app
from src.components.data_drawer.header import data_drawer_header

def create_chart_header_from_source(selected_marker, theme):
    type = selected_marker.get("type")
    if type == "Note":
        header = None

    elif type == "Environment":
        d = Environment(selected_marker["data"])
        props = get_source_props("Environment")
        header = data_drawer_header(
            props["name"], 
            [], 
            props["marker"], 
            theme) 
    else:
        d = Deployment(selected_marker["data"])
        props = get_source_props(d.node_type)
        header = data_drawer_header(
                title=props["name"], 
                tags=d.tags, 
                icon=props["marker"], 
                theme=theme, 
                desc=d.node_label)
    return header


def create_chart_from_source(selected_marker, date_range, theme, notes, environment_data, tz):
    marker_data    = selected_marker.get("data")
    marker_id      = marker_data.get("id")
    drawer_content = html.Div("Somthing went wrong, not device found!")
    
    match selected_marker.get("type"):
        case "Audio Logger":
            drawer_content = create_audio_chart(marker_data, date_range, theme)
        case "Env Sensor":
            drawer_content = create_env_chart(marker_data, theme)
        case "Pax Counter":
            drawer_content = create_pax_chart(marker_data, date_range, theme)
        case "Pollinator Cam":
            drawer_content = create_pollinator_chart(marker_data, date_range, theme)
        case "Environment":
            drawer_content = create_environment_point_chart(environment_data["legend"], marker_id, theme)
        case "Note":
            for note in notes["entries"]:
                if note["id"] == marker_id:
                    n = Note(note)
                    drawer_content = note_view(n, theme, tz)
    return drawer_content



def chart_drawer(args, device, all_notes, env):
    # initially show chart of device, if a node_label is set in the query params
    notes = {}
    notes["entries"] = all_notes
    
    chart = []
    header = []
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


        chart = create_chart_from_source(
                active_device,
                {"start": start, "end": end},
                "light",
                notes,
                env,
                None,
                )
        header = create_chart_header_from_source(active_device, "light")
        drawer_state = True

    return dmc.Drawer(
        opened=drawer_state,
        id=ID_CHART_DRAWER,
        zIndex=100,
        size=CHART_DRAWER_HEIGHT,
        closeOnClickOutside=True,
        withCloseButton=False,
        closeOnEscape=False,
        withOverlay=False,
        position="bottom",
        styles={"content": {"background": BACKGROUND_COLOR}, "body": {"paddingBottom": 0}},
        children=[
            html.Div(id=ID_CHART_DRAWER_HEADER, children=header),
            dcc.Loading(
                id=ID_LOADER,
                type="default",
                color="#6c9d9d",
                children=html.Div(
                id=ID_CHART_CONTAINER, 
                children=chart
                ))
            ],
    )


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_NOTIFICATION, "children", allow_duplicate=True),
    Output(ID_LOADER, "visible", allow_duplicate=True),
    Output(ID_CHART_DRAWER_HEADER, "children"),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    State(ID_APP_THEME, "forceColorScheme"),
    prevent_initial_call=True
)
def open_drawer(selected_marker, theme):
    if selected_marker is None:
        raise PreventUpdate

    if selected_marker["type"] in DATA_SOURCES_WITHOUT_CHART_SUPPORT:
        n = notification("No chart available for this device type.", NotificationType.INFO)
        return False, n, False, no_update

    type = selected_marker["type"]
    if type == "Note":
        header = None

    elif type == "Environment":
        d = Environment(selected_marker["data"])
        props = get_source_props("Environment")
        header = data_drawer_header(
            props["name"], 
            [], 
            props["marker"], 
            theme) 
    else:
        d = Deployment(selected_marker["data"])
        props = get_source_props(d.node_type)
        selected_marker = dict(data=d.to_dict(), type=d.node_type)    
        header = create_chart_header_from_source(selected_marker, theme)

    return True, no_update, True, header



@app.callback(
    Output(ID_CHART_CONTAINER, "children"),
    Output(ID_LOADER, "visible", allow_duplicate=True),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    Input(ID_DATE_RANGE_STORE, "data"),
    Input(ID_APP_THEME, "forceColorScheme"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State({"role": "Environment", "label": "Store", "type": "virtual"}, "data"),
    State(ID_TIMEZONE_STORE, "data"),
    prevent_initial_call=True
)
def update_drawer_content_from_marker_store(selected_marker, date_range, theme, notes, environment_data, tz):
    if selected_marker is None:
        raise PreventUpdate

    drawer_content = create_chart_from_source(
        selected_marker,
        date_range,
        theme,
        notes,
        environment_data,
        tz["tz"],
        )

    return drawer_content, False


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
    Output(ID_LOGO_CONTAINER, "style"),
    Output(ID_CHART_DRAWER, "styles"),
    Input(ID_SETTINGS_DRAWER, "opened"),
    Input(ID_APP_THEME, "forceColorScheme"),
    State(ID_CHART_DRAWER, "styles"),
)
def settings_drawer_state(opened, scheme, styles):
    width_reduced = {"width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}
    full_width = {"width": "100vw"}

    srinked = { "inner": {"width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px", "left": f"{SETTINGS_DRAWER_WIDTH}px"}}
    expanded = {"inner": {"width": "100vw", "left": 0}}

    styles.update({"content": {
        "background": DEFAULT_THEME["colors"]["dark"][7] if scheme == "dark" else BACKGROUND_COLOR,
        }})

    if opened:
        styles.update(srinked)
        return width_reduced, styles
    styles.update(expanded)
    return full_width, styles 
