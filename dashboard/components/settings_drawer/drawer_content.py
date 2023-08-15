import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, State

from dashboard.components.settings_drawer.components.date_time_section import date_time_section
from dashboard.components.settings_drawer.components.general_controls import general_controls
from dashboard.components.settings_drawer.components.tag_filter import tag_filter
from dashboard.components.settings_drawer.components.source_filter import source_filter
from dashboard.components.settings_drawer.components.marker_popup import environment_popup, marker_popup
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.deployment import Deployment
from dashboard.model.environment import Environment
from dashboard.model.note import Note
from util.functions import was_deployed


def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md")


def drawer_content(node_types, tags_data, depl_markers):
    return dmc.Container(
        children=[
            dmc.Space(h=30),
            dmc.ScrollArea([
                html.Div([
                    divider("Date Range"),
                    date_time_section(),
                    divider("Data Source"),
                    source_filter(node_types, depl_markers),
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
    Input(ID_DATE_RANGE_PICKER, "value"),
    State(ID_DEPLOYMENT_MARKER_STORE, "data"),
    State(ID_DEPLOYMENT_DATA_STORE, "data"),
)
def add_device_markers(checkboxes, tags, fs_tag, time_range, colors, deployment_data):
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
        depl_to_show[key] = list(filter(lambda x: was_deployed(x, time_range[0], time_range[1]), depl_to_show[key]))

    markers = []

    for key in depl_to_show.keys():
        for d in depl_to_show[key]:
            markers.append(
                dl.Marker(
                    position=[d.lat, d.lon],
                    children=[
                        dl.Popup(
                            children=[marker_popup(d, colors[d.node_type]['color'])],
                            closeButton=False,
                            id=f"{d.deployment_id}"
                        ),
                        dl.Tooltip(
                            children=f"{d.node_type}\n{d.node_label}",
                            offset={"x": -10, "y": 2},
                            direction="left",
                        ),
                    ],
                    icon=dict(iconUrl=colors[d.node_type]['svgPath'], iconAnchor=[15, 6], iconSize=30),
                    id={"role": f"{d.node_type}", "id": d.deployment_id, "label": d.node_label, "lat": d.lat,  "lon": d.lon},
                )
            )
    return markers


@app.callback(
    Output(ID_ENV_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    State(ID_ENV_DATA_STORE, "data"),
)
def add_environment_markers(values, data):
    if "Environment Data Point" not in values:
        return []
    markers = []

    for e in data:
        e = Environment(e)
        markers.append(
            dl.Marker(
                position=[e.lat, e.lon],
                children=[
                    dl.Popup(
                        children=[environment_popup(e)],
                        closeButton=False
                    ),
                    dl.Tooltip(
                        children=f"Environment Data: {e.environment_id}",
                        offset={"x": -10, "y": 2},
                        direction="left",
                    ),
                ],
                icon=dict(iconUrl="assets/markers/environment.svg", iconAnchor=[15, 6], iconSize=30),
                id={"role": "Environment", "id": e.environment_id, "label": "", "lat": e.lat,  "lon": e.lon},
            )
        )
    return markers


@app.callback(
    Output(ID_NOTES_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    State(ID_NOTES_STORE, "data"),
)
def add_note_markers(values, data):
    if "Notes" not in values:
        return []
    markers = []

    for n in data:
        n = Note(n)
        markers.append(
            dl.Marker(
                position=[n.lat, n.lon],
                children=[
                    dl.Popup(
                        # children=[environment_popup(n)],
                        closeButton=False
                    ),
                    dl.Tooltip(
                        children=f"Note: {n.note_id}",
                        offset={"x": -10, "y": 2},
                        direction="left",
                    ),
                ],
                icon=dict(iconUrl="assets/markers/note.svg", iconAnchor=[15, 6], iconSize=30),
                id={"role": "Note", "id": n.note_id, "label": "", "lat": n.lat,  "lon": n.lon},
            )
        )
    return markers
