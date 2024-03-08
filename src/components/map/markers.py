import dash_leaflet as dl
from dash import (
    Output,
    Input,
    State,
    ALL,
    html,
    clientside_callback,
    ClientsideFunction,
)
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dash_extensions.javascript import assign

from src.components.settings_drawer.components.marker_popup import environment_popup, device_popup, note_tooltip
from src.config.id_config import *
from src.config.map_config import get_source_props
from src.main import app
from src.model.deployment import Deployment
from src.model.environment import Environment
from src.model.note import Note
from src.util.helper_functions import was_deployed


@app.callback(
    Output(ID_MAP_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_TAG_CHIPS_GROUP, "value"),
    Input(ID_FS_TAG_CHIPS_GROUP, "value"),
    Input(ID_DATE_RANGE_STORE, "data"),
    Input({"role": ALL, "label": "Store", "type": "physical"}, "data"),
    prevent_initial_call=True
)
def add_device_markers(checkboxes, tags, fs_tag, time_range, sources):
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

    # parse to json objects
    for key in deployment_data:
        deployment_data[key] = list(map(lambda depl: Deployment(depl), deployment_data[key]))

    depl_to_show = {}
    # type filter
    for active in checkboxes:
        # depl_to_show:  {"key": [Deployments]
        depl_to_show[active] = deployment_data[active]

    depl_fs_filtered = {}
    # field study tag filter
    if fs_tag:
        for key in depl_to_show.keys():
            depl_fs_filtered[key] = list(filter(lambda depl: fs_tag in depl.tags or fs_tag == "ANY", depl_to_show[key]))

    depl_tags_filtered = {}
    if tags:
        for key in depl_to_show.keys():
            depl_tags_filtered[key] = list(filter(lambda depl: any(tag in depl.tags for tag in tags), depl_to_show[key]))

    for key in depl_to_show.keys():
        fs_tags = depl_fs_filtered.get(key, [])
        tags = depl_tags_filtered.get(key, []) 
        depl_to_show[key] = fs_tags + tags

    # time filter
    for key in depl_to_show.keys():
        depl_to_show[key] = list(filter(lambda x: was_deployed(x, time_range["start"], time_range["end"]), depl_to_show[key]))

    markers = []

    for key in depl_to_show.keys():
        for d in depl_to_show[key]:
            markers.append(
                dl.Marker(
                    position=[d.lat, d.lon],
                    children=[
                        dl.Popup(
                            children=[device_popup(d, get_source_props(d.node_type)["color"])],
                            closeButton=False,
                            id=f"{d.id}",
                            autoPan=False
                        ),
                        dl.Tooltip(
                            children=f"{d.node_type}\n{d.node_label}",
                            offset={"x": -10, "y": 2},
                            direction="left",
                        ),
                    ],
                    icon=dict(iconUrl=get_source_props(d.node_type)["marker"], iconAnchor=[15, 6], iconSize=[30, 30]),
                    id={"role": f"{d.node_type}", "id": d.id, "label": "Node"},
                )
            )
    return markers


@app.callback(
    Output(ID_ENV_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input({"role": "Environment Data Point", "label": "Store", "type": "virtual"}, "data"),
)
def add_environment_markers(active_checkboxes, all_environments):
    if "Environment Data Point" not in active_checkboxes:
        return []
    markers = []

    for env in all_environments["entries"]:
        env = Environment(env)
        markers.append(
            dl.Marker(
                position=[env.lat, env.lon],
                children=[
                    dl.Popup(
                        children=[environment_popup(env)],
                        closeButton=False,
                        autoPan=False
                    ),
                    dl.Tooltip(
                        children=f"Environment Data: {env.id}",
                        offset={"x": -10, "y": 2},
                        direction="left",
                    ),
                ],
                icon=dict(iconUrl=get_source_props("Environment Data Point")["marker"], iconAnchor=[15, 6], iconSize=[30, 30]),
                id={"role": "Environment Data Point", "id": env.id, "label": "Node"},
            )
        )
    return markers


@app.callback(
    Output(ID_NOTES_LAYER_GROUP, "children", allow_duplicate=True),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_SELECTED_NOTE_STORE, "data"),
    Input({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    prevent_initial_call=True
)
def add_note_markers(active_checkboxes, selected_note, all_notes):
    if "Note" not in active_checkboxes:
        return []

    marker_icon           = dict(iconUrl=get_source_props("Note")["marker"], iconAnchor=[15, 6],  iconSize=[30, 30])
    marker_icon_draggable = dict(iconUrl="assets/markers/note_move.svg",     iconAnchor=[61, 50], iconSize=[120, 120])

    all_notes = all_notes.get("entries", [])
    selected_note_id = None

    if selected_note["data"] is not None:
        for note in all_notes:
            if note["id"] == selected_note["data"]["id"]:
                selected_note_id = note["id"]
                note["location"]["lat"] = selected_note["data"]["location"]["lat"]
                note["location"]["lon"] = selected_note["data"]["location"]["lon"]

    markers = []
    dragend_clbk = dict(dragend=assign('function(e, ctx){ctx.setProps({latlng: {lat: `${e.target.getLatLng()["lat"], lng:`${e.target.getLatLng()["lng"]`})}')) 

    for note in all_notes:
        current_note = Note(note)
        in_edit_mode = current_note.id == selected_note_id
        markers.append(
            dl.Marker(
                position=[current_note.lat, current_note.lon],
                children=[
                    dl.Popup(
                        children=current_note.title,
                        closeButton=False,
                        autoPan=False,
                    ),
                    dl.Tooltip(
                        children=note_tooltip(current_note),
                        offset={"x": -10, "y": 2},
                        direction="left",
                        className="marker-tooltip",
                    ),
                ],
                icon=marker_icon_draggable if in_edit_mode else marker_icon,
                eventHandlers=dragend_clbk if in_edit_mode else {},
                draggable=True if in_edit_mode else False,
                id={"role": "Note", "id": current_note.id, "label": "Node"},
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
    moving_zone_bounds = [[10, 20],[30, 20]] 

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




