import json
from datetime import datetime, timedelta

import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, State
from dash_iconify import DashIconify

from dashboard.components.left_drawer.components.general_controls import general_controls
from dashboard.components.left_drawer.components.date_time_section import date_time_section
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
                    divider("Time Range Selection"),
                    date_time_section(),

                    divider("Filter"),
                    type_filter(node_types, depl_colors),
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


# callback ordering matters!
@app.callback(
    Output(ID_DATE_RANGE_PICKER, "value"),
    Input(ID_DATE_RANGE_SEGMENT, "value"),
)
def update_picker_from_segment(segment_data):
    if not segment_data:
        seg_time_range = 7
    else:
        seg_time_range = int(segment_data)

    return [datetime.now().date() - timedelta(weeks=seg_time_range), datetime.now().date()]


@app.callback(
    Output(ID_MAP_LAYER_GROUP, "children"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_TAG_CHIPS_GROUP, "value"),
    Input(ID_DATE_RANGE_PICKER, "value"),
    State(ID_DEPLOYMENT_COLOR_STORE, "data"),
    State(ID_DEPLOYMENT_DATA_STORE, "data"),
)
def filter_map_data(checkboxes, chips, time_range, colors, deployment_data):
    checkboxes = list(filter(lambda c: c != "all", checkboxes))

    depl_to_show = {}

    # parse to json objects
    for key in deployment_data:
        deployment_data[key] = map(lambda d: Deployment(d), deployment_data[key])

    # checkbox filter
    for active in checkboxes:
        # depl_to_show:  {"key": [Deployments]
        depl_to_show[active] = deployment_data[active]

    # chip filter
    if chips:
        for key in depl_to_show.keys():
            depl_to_show[key] = filter(lambda d: any(item in chips for item in d.tags), depl_to_show[key])

    # time filter
    for key in depl_to_show.keys():
        depl_to_show[key] = filter(lambda x: was_deployed(x, time_range[0], time_range[1]), depl_to_show[key])

    markers = []

    for key in depl_to_show.keys():
        for d in depl_to_show[key]:
            markers.append(dl.DivMarker(
                children=[
                    DashIconify(
                        icon="ion:location-sharp",
                        height=24,
                        color=f"{colors[d.node_type]}"
                    ),
                    dl.Tooltip(f"{d.node_type}\n{d.node_label}"),
                ],
                iconOptions=dict(className="div-icon", iconAnchor=[32, 16]),
                position=[d.lat, d.lon],
                id={"role": f"{d.node_type}", "id": d.deployment_id, "label": d.node_label},
            ))

    return markers
