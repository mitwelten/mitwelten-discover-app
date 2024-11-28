import dash_mantine_components as dmc
from dash_mantine_components import DEFAULT_THEME
from dash import Output, Input, html, State, no_update, ctx, dcc
from dash.exceptions import PreventUpdate
from src.components.data_drawer.types.wild_cam import create_wild_cam_chart
from src.model.base import BaseDeployment
from src.model.url_parameter import UrlParameter
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
from src.config.app_config import (
    BACKGROUND_COLOR,
    CHART_DRAWER_HEIGHT,
    SETTINGS_DRAWER_WIDTH,
    EXCLUDED_DEPLOYMENTS,
)
from src.config.id_config import *
from src.main import app
from src.components.data_drawer.header import data_drawer_header


def create_chart_header_from_source(selected_marker, theme):
    type_ = selected_marker.get("type")
    if type_ == "Note":
        return None

    props = get_source_props(type_)
    data_class = Environment if type_ == "Environment" else Deployment
    data_instance = data_class(selected_marker["data"])

    return data_drawer_header(
        title=props["name"],
        tags=getattr(data_instance, "tags", []),
        icon=props["marker"],
        theme=theme,
        desc=getattr(data_instance, "node_label", ""),
    )


def create_chart_from_source(selected_marker, date_range, theme, notes, environment_data, tz):
    marker_data = selected_marker.get("data")
    marker_id = marker_data.get("id")
    type_ = selected_marker.get("type")

    chart_functions = {
        "Audio Logger": create_audio_chart,
        "Env Sensor": create_env_chart,
        "Pax Counter": create_pax_chart,
        "Pollinator Cam": create_pollinator_chart,
        "Wild Cam": create_wild_cam_chart,
    }

    if type_ in chart_functions:
        return chart_functions[type_](marker_data, date_range, theme)
    elif type_ == "Environment":
        return create_environment_point_chart(environment_data["legend"], marker_id, theme)
    elif type_ == "Note":
        note_data = next((note for note in notes["entries"] if note["id"] == marker_id), None)
        if note_data:
            note_instance = Note(note_data)
            return note_view(note_instance, theme, tz)
    return html.Div("Etwas ist schiefgelaufen, kein Gerät gefunden!")


def chart_drawer(params: UrlParameter, device: BaseDeployment | None, all_notes, env):
    notes = {"entries": all_notes}
    chart = []
    header = []
    drawer_state = False

    if device:
        active_device = {"type": device.type, "data": device.to_dict()}
        chart = create_chart_from_source(
            active_device, {"start": params.start, "end": params.end}, "light", notes, env, None
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
        styles={
            "content": {"background": BACKGROUND_COLOR},
            "body": {"paddingBottom": 0},
        },
        children=[
            html.Div(id=ID_CHART_DRAWER_HEADER, style={"maxWidth": "1200px"}, children=header),
            dcc.Loading(
                id=ID_LOADER,
                type="default",
                color="#6c9d9d",
                children=html.Div(
                    id=ID_CHART_CONTAINER, style={"maxWidth": "1200px"}, children=chart
                ),
            ),
        ],
    )


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_NOTIFICATION, "children", allow_duplicate=True),
    Output(ID_LOADER, "visible", allow_duplicate=True),
    Output(ID_CHART_DRAWER_HEADER, "children"),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    State(ID_APP_THEME, "forceColorScheme"),
    prevent_initial_call=True,
)
def open_drawer(selected_marker, theme):
    if not selected_marker:
        raise PreventUpdate

    type_ = selected_marker["type"]
    if type_ in EXCLUDED_DEPLOYMENTS:
        n = notification("Für diesen Gerätetyp ist kein Diagramm verfügbar.", NotificationType.INFO)
        return False, n, False, no_update

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
    prevent_initial_call=True,
)
def update_drawer_content_from_marker_store(
    selected_marker, date_range, theme, notes, environment_data, tz
):
    if not selected_marker.get("data") or not ctx.triggered_id:
        raise PreventUpdate

    drawer_content = create_chart_from_source(
        selected_marker, date_range, theme, notes, environment_data, tz["tz"]
    )

    return drawer_content, False


@app.callback(
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_EDIT_NOTE_STORE, "data"),
    prevent_initial_call=True,
)
def activate_preventing_marker_clicks(selected_note):
    state = bool(selected_note["data"])
    return {"state": state}


@app.callback(
    Output(ID_LOGO_CONTAINER, "style"),
    Output(ID_CHART_DRAWER, "styles"),
    Input(ID_SETTINGS_DRAWER, "opened"),
    Input(ID_APP_THEME, "forceColorScheme"),
    State(ID_CHART_DRAWER, "styles"),
)
def settings_drawer_state(opened, scheme, styles):
    width = f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px)" if opened else "100vw"
    left = f"{SETTINGS_DRAWER_WIDTH}px" if opened else "0"

    styles.update(
        {
            "content": {
                "background": DEFAULT_THEME["colors"]["dark"][7]
                if scheme == "dark"
                else BACKGROUND_COLOR
            },
            "inner": {"width": width, "left": left},
        }
    )

    logo_style = {"width": width}
    return logo_style, styles
