from datetime import datetime, timedelta

import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, State

from dashboard.components.left_drawer.components.date_time_section import date_time_section
from dashboard.components.left_drawer.components.general_controls import general_controls
from dashboard.components.left_drawer.components.tag_filter import tag_filter
from dashboard.components.left_drawer.components.type_filter import type_filter
from dashboard.config.id_config import *
from dashboard.maindash import app
from dashboard.model.deployment import Deployment
from util.functions import was_deployed

header = dmc.Center(dmc.Text("Mitwelten Discover", size="lg"))


def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md")


def settings_content(node_types, tags_data, depl_colors):
    return dmc.Container(
        children=[
            header,
            dmc.Space(h=30),
            dmc.ScrollArea([
                html.Div([
                    divider("Date Range"),
                    date_time_section(),

                    divider("Device Type"),
                    type_filter(node_types, depl_colors),
                    divider("Tags"),
                    tag_filter(tags_data),
                    dmc.Space(h=30),

                    divider("Settings"),
                    general_controls(),
                ],
                    id=ID_LEFT_DRAWER_CONTENT_SCROLL_AREA,
                )],
                offsetScrollbars=True,
                type="always"
            )],
        fluid=True,
        style={"height": "100vh"}
    )




@app.callback(
    Output(ID_MAP_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_TAG_CHIPS_GROUP, "value"),
    Input(ID_FS_TAG_CHIPS_GROUP, "value"),
    Input(ID_DATE_RANGE_PICKER, "value"),
    State(ID_DEPLOYMENT_COLOR_STORE, "data"),
    State(ID_DEPLOYMENT_DATA_STORE, "data"),
)
def filter_map_data(checkboxes, tags, fs_tags, time_range, colors, deployment_data):
    print(checkboxes)
    checkboxes = list(filter(lambda c: c != "all", checkboxes))

    depl_to_show = {}

    # parse to json objects
    for key in deployment_data:
        deployment_data[key] = list(map(lambda depl: Deployment(depl), deployment_data[key]))


    # checkbox filter
    for active in checkboxes:
        # depl_to_show:  {"key": [Deployments]
        depl_to_show[active] = deployment_data[active]


    # chip filter
    tags = tags + fs_tags
    if tags:
        for key in depl_to_show.keys():
            depl_to_show[key] = list(filter(lambda depl: any(item in tags for item in depl.tags), depl_to_show[key]))

    # time filter
    for key in depl_to_show.keys():
        depl_to_show[key] = list(filter(lambda x: was_deployed(x, time_range[0], time_range[1]), depl_to_show[key]))

    markers = []

    for key in depl_to_show.keys():
        for d in depl_to_show[key]:
            markers.append(
                dl.Marker(
                    position=[d.lat, d.lon],
                    children=dl.Tooltip(children=f"{d.node_type}\n{d.node_label}", offset={"x": 25, "y": -15}),
                    icon=dict(iconUrl=colors[d.node_type]['svgPath'], iconAnchor=[32, 16], iconSize=30),
                    id={"role": f"{d.node_type}", "development_id": d.deployment_id, "label": d.node_label},
                )
            )
    return markers
