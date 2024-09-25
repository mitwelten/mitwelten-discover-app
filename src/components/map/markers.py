import dash_leaflet as dl
import re
from dash import (
    Output,
    Input,
    ctx,
    State,
    ALL,
    clientside_callback,
    ClientsideFunction,
    no_update
)
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import assign

from src.components.settings_drawer.components.marker_popup import environment_popup, device_popup, note_popup
from src.config.id_config import *
from src.config.map_config import get_source_props
from src.main import app
from src.model.deployment import Deployment
from src.model.environment import Environment
from src.model.note import Note
from src.util.helper_functions import was_deployed

from src.url.parse import update_query_data
from pprint import pprint

popup_events=dict(
    mouseout  = assign("", "mouseout"),
    click     = assign("", "click"),
    mouseover = assign("", "mouseover"), 
) 

@app.callback(
    Output(ID_DEPLOYMENT_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_TAGS, "value"),
    Input(ID_DATE_RANGE_STORE, "data"),
    Input({"role": ALL, "label": "Store", "type": "physical"}, "data"),
    Input(ID_TIMEZONE_STORE, "data"),
    Input(ID_DEVICE_SELECT, "value"),
    prevent_initial_call=True
)
def add_device_markers(checkboxes, tags, time_range, sources, timezone, device_select):
    """
    Changes the visible markers of the "physical" devices on the map.
    This callback is mainly triggered by adjusting the filter settings.

    :param checkboxes: The activated checkboxes of the data sources.
    :param tags: The selected additional tags.
    :param fs_tag: The selected field study (fs) tag.
    :param time_range: The selected date range.
    :param sources: The store containing "physical" sources, which are represented by deployments.
    :return: The map layer containing all current visible markers with the selected settings.
    """

    deployment_data = {}
    for source in sources:
        deployment_data[source["type"]] = source["entries"]

    checkboxes = list(filter(lambda c: c in deployment_data.keys(), checkboxes))

    visible_deployments: list[Deployment] = []
    if tags is None:
        tags = []

    predicate = re.compile(r'\d{4}-\d{4}')

    # type filter
    for active in checkboxes:
        for d in deployment_data[active]:
            d = Deployment(d)

            tag_filter = True
            for t in tags:
                if t not in d.tags:
                    tag_filter = False
                    break

            if tag_filter: 
                visible_deployments.append(d)

    # time filter
        visible_deployments = list(filter(lambda x: was_deployed(x, time_range["start"], time_range["end"]), visible_deployments))
        if device_select is not None and predicate.match(device_select):
            visible_deployments = list(filter(lambda x: x.node_label == device_select, visible_deployments))

    markers = []

    for d in visible_deployments:
        markers.append(
                dl.Marker(
                    position=[d.lat, d.lon],
                    children=[
                        dl.Popup(
                            children=device_popup(d, timezone.get("tz")),
                            closeButton=False,
                            id=f"{d.id}",
                            autoPan=False,
                            autoClose=False,
                            ),
                        ],
                    eventHandlers=popup_events,
                    icon=dict(iconUrl=get_source_props(d.node_type)["marker"], iconAnchor=[15, 6], iconSize=[30, 30]),
                    id={"role": f"{d.node_type}", "id": d.id, "label": "Node"},
                    )
            )

    return markers

@app.callback(
    Output(ID_ENV_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input({"role": "Environment", "label": "Store", "type": "virtual"}, "data"),
    Input(ID_TIMEZONE_STORE, "data"),
    prevent_initial_call=True
)
def add_environment_markers(active_checkboxes, all_environments, timezone):
    if "Environment" not in active_checkboxes:
        return []

    envs = all_environments["entries"]
    markers = []

    for env in envs:
        env = Environment(env)
        marker = dl.Marker(
                position=[env.lat, env.lon],
                children=[
                    dl.Popup(
                        children=[environment_popup(env, timezone.get("tz"))],
                        closeButton=False,
                        autoPan=False,
                        autoClose=False,
                        ),
                    ],
                eventHandlers=popup_events,
                icon=dict(iconUrl=get_source_props("Environment")["marker"], iconAnchor=[15, 6], iconSize=[30, 30]),
                id={"role": "Environment", "id": env.id, "label": "Node"},

                )
        markers.append(marker)

    return markers


@app.callback(
    Output(ID_NOTES_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_EDIT_NOTE_STORE, "data"),
    Input({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    Input(ID_TAGS, "value"),
    Input(ID_TIMEZONE_STORE, "data"),
    prevent_initial_call=True
)
def add_note_markers(active_checkboxes, selected_note, all_notes, tags, timezone):
    if "Note" not in active_checkboxes:
        return []

    marker_icon           = dict(iconUrl=get_source_props("Note")["marker"], iconAnchor=[15, 6],  iconSize=[30, 30])
    marker_icon_draggable = dict(iconUrl="assets/markers/docu_move.svg",     iconAnchor=[31, 14], iconSize=[60, 60])

    all_notes = all_notes.get("entries", [])
    visible_notes = set()

    selected_note_id = None
    if selected_note is not None and selected_note.get("data") is not None:
        selected_note = selected_note.get("data")
        selected_note_id = selected_note.get("id")

    for note in all_notes:
        n = Note(note)
        tag_filter = True
        for t in tags:
            if t not in n.tags:
                tag_filter = False
                break
        if tag_filter:
            visible_notes.add(n)

        if n.id == selected_note_id:
            n.lat = selected_note.get("location", {}).get("lat")
            n.lon = selected_note.get("location", {}).get("lon")


    markers = []

    for note in visible_notes:
        in_edit_mode = note.id == selected_note_id
        if in_edit_mode:
            popup_events["dragend"] = assign("", "setLatLng")
        markers.append(
            dl.Marker(
                position=[note.lat, note.lon],
                children=[
                    dl.Popup(
                        children=note_popup(note, timezone.get("tz")),
                        closeButton=False,
                        autoPan=False,
                        autoClose=False,
                        ),
                ],
                icon=marker_icon_draggable if in_edit_mode else marker_icon,
                eventHandlers=popup_events,
                draggable=True if in_edit_mode else False,
                id={"role": "Note", "id": note.id, "label": "Node"},
            )
        )

    return markers


clientside_callback(
    ClientsideFunction(
        namespace="browser_properties", function_name="fetchWindowProps"
    ),
    Output(ID_BROWSER_PROPERTIES_STORE, "data"),
    Input(ID_SELECTED_MARKER_STORE, "data"),
)


@app.callback(
    Output(ID_MAP, "viewport", allow_duplicate=True),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    Input(ID_CHART_DRAWER, "size"),
    State(ID_BROWSER_PROPERTIES_STORE, "data"),
    State(ID_SETTINGS_DRAWER, "opened"),
    State(ID_SETTINGS_DRAWER, "size"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_MAP, "bounds"),
    State(ID_MAP, "zoom"),
    State(ID_MAP, "center"),
    prevent_initial_call=True,
)
def ensure_marker_visibility_in_viewport(
    marker,
    _,
    browser_props,
    drawer_state,
    settings_drawer_size,
    data_drawer_size,
    bounds,
    zoom,
    center,
):
    if marker is None:
        raise PreventUpdate

    if bounds is None:
        raise PreventUpdate

    top    = bounds[1][0]
    bottom = bounds[0][0]
    left   = bounds[0][1]
    right  = bounds[1][1]

    # visibile map distance in grad
    map_delta_lat = top - bottom
    map_delta_lon = right - left

    # set drawer size to 1 if the settings drawer is closed
    settings_drawer_size = 1 if not drawer_state else settings_drawer_size

    # the height of the data drawer in grad
    data_drawer_height = map_delta_lat   / browser_props["height"] * data_drawer_size

    # the width of the settings drawer in grad
    settings_drawer_width = map_delta_lon / browser_props["width"]  * settings_drawer_size

    # the range, in which markers are moved to the center in %
    moving_zone_bounds = [[10, 20],[40, 20]] 

    zone_factor_h = (top - (bottom + data_drawer_height)) / 100
    zone_factor_w = (right - (left + settings_drawer_width)) / 100

    ok_zone = [
        [bottom + data_drawer_height + moving_zone_bounds[0][0] * zone_factor_h, left + settings_drawer_width + moving_zone_bounds[0][1] * zone_factor_w],
        [top - moving_zone_bounds[1][0] * zone_factor_h, right -  moving_zone_bounds[1][1] * zone_factor_w]
         ]

    marker_loc = marker["data"]["location"]

    # returns an array containing the values to be moved: [[bottom/top], [left/right]]
    def check_marker_pos(marker_loc, ok_zone):
        overlapping = [0,0]
        # bottom
        if marker_loc["lat"] < ok_zone[0][0]: 
            overlapping[0] = ok_zone[0][0] - marker_loc["lat"]
        # top
        if marker_loc["lat"] > ok_zone[1][0]: 
            overlapping[0] = ok_zone[1][0] - marker_loc["lat"]
        # left
        if marker_loc["lon"] < ok_zone[0][1]:
            overlapping[1] = ok_zone[0][1] - marker_loc["lon"]
        # right
        if marker_loc["lon"] > ok_zone[1][1]:
            overlapping[1] = ok_zone[1][1] - marker_loc["lon"]
        return overlapping

    move_required = check_marker_pos(marker_loc, ok_zone)

    new_center = [center["lat"] + (move_required[0] * -1), center["lng"] + (move_required[1] * -1)]

    return dict(center=new_center, zoom=zoom, transition="flyTo")




