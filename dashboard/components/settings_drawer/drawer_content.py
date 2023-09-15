from pprint import pprint

import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, State, ALL
from dash.exceptions import PreventUpdate

from dashboard.components.settings_drawer.components.date_time_section import date_time_section
from dashboard.components.settings_drawer.components.general_controls import general_controls
from dashboard.components.settings_drawer.components.marker_popup import environment_popup, device_popup, note_popup
from dashboard.components.settings_drawer.components.source_filter import source_filter
from dashboard.components.settings_drawer.components.tag_filter import tag_filter
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.deployment import Deployment
from dashboard.model.environment import Environment
from dashboard.model.note import Note
from dashboard.util.helper_functions import was_deployed


def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md")


def drawer_content(deployments, tags_data, data_sources):
    return dmc.Container(
        children=[
            dmc.Space(h=30),
            dmc.ScrollArea([
                html.Div([
                    divider("Date Range"),
                    date_time_section(),
                    divider("Data Source"),
                    source_filter(deployments, data_sources),
                    divider("Tags"),
                    tag_filter(tags_data),
                    divider("Settings"),
                    general_controls(),
                ],
                    id=ID_LEFT_DRAWER_CONTENT_SCROLL_AREA,
                    style={"height": "100%"}
                )],
                offsetScrollbars=True,
                type="always",
                style={"height": "100%"}
            )],
        fluid=True,
        style={"height": "calc(100vh - 100px)"}
    )


@app.callback(
    Output(ID_MAP_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_TAG_CHIPS_GROUP, "value"),
    Input(ID_FS_TAG_CHIPS_GROUP, "value"),
    Input(ID_DATE_RANGE_STORE, "data"),
    State(ID_DATA_SOURCE_STORE, "data"),
    State({"role": ALL, "label": "Store", "type": "physical"}, "data"),
)
def add_device_markers(checkboxes, tags, fs_tag, time_range, colors, sources):
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
    # tag filter
    if fs_tag:
        for key in depl_to_show.keys():
            depl_fs_filtered[key] = list(filter(lambda depl: fs_tag in depl.tags, depl_to_show[key]))

    depl_tags_filtered = {}
    if tags:
        for key in depl_to_show.keys():
            depl_tags_filtered[key] = list(filter(lambda depl: any(item in depl.tags for item in tags), depl_to_show[key]))

    for key in depl_to_show.keys():
        fs_tags = depl_fs_filtered.get(key) if depl_fs_filtered.get(key) is not None else []
        tags = depl_tags_filtered.get(key) if depl_tags_filtered.get(key) is not None else []
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
                            children=[device_popup(d, colors[d.node_type]['color'])],
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
                    icon=dict(iconUrl=colors[d.node_type]['svgPath'], iconAnchor=[15, 6], iconSize=30),
                    id={"role": f"{d.node_type}", "id": d.id, "label": "Node"},
                )
            )
    return markers


@app.callback(
    Output(ID_ENV_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    State({"role": "Environment Data Point", "label": "Store", "type": "virtual"}, "data"),
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
                icon=dict(iconUrl="assets/markers/environment.svg", iconAnchor=[15, 6], iconSize=30),
                id={"role": "Environment Data Point", "id": env.id, "label": "Node"},
            )
        )
    return markers


@app.callback(
    Output(ID_NOTES_LAYER_GROUP, "children", allow_duplicate=True),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_SELECTED_NOTE_STORE, "data"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    prevent_initial_call=True
)
def add_note_markers(active_checkboxes, selected_note, all_notes):
    print("callback: marker update")
    if "Note" not in active_checkboxes:
        return []

    marker_icon = dict(iconUrl="assets/markers/note.svg", iconAnchor=[15, 6], iconSize=30)
    marker_icon_draggable = dict(iconUrl="assets/markers/note_move.svg", iconAnchor=[61, 50], iconSize=120)

    all_notes = all_notes["entries"]
    if selected_note["data"] is not None:
        found = False
        for note in all_notes:
            if note["id"] == selected_note["data"]["id"]:
                found = True
                print(f"print marker: selected note: {selected_note['data']['id']} is in edit mode: {selected_note['inEditMode']}")
                note["inEditMode"] = selected_note["inEditMode"]
                note["location"]["lat"] = selected_note["data"]["location"]["lat"]
                note["location"]["lon"] = selected_note["data"]["location"]["lon"]

        if not found:
            selected_note = selected_note["data"]
            selected_note["inEditMode"] = True
            all_notes.append(selected_note)

    markers = []
    for note in all_notes:
        current_note = Note(note)
        in_edit_mode = note.get("inEditMode") is not None and note["inEditMode"]
        markers.append(
            dl.Marker(
                position=[current_note.lat, current_note.lon],
                children=[
                    dl.Popup(
                        children=[note_popup(current_note)],
                        closeButton=False,
                        autoPan=False
                    ),
                    dl.Tooltip(
                        children=f"Note: {current_note.id}",
                        offset={"x": -10, "y": 2},
                        direction="left",
                    ),
                ],
                icon=marker_icon_draggable if in_edit_mode else marker_icon,
                draggable=True if in_edit_mode else False,
                id={"role": "Note", "id": current_note.id, "label": "Node"},
            )
        )
    return markers
