import json
from datetime import datetime, timedelta

import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, callback
from dash_iconify import DashIconify

from dashboard.components.chart_modal.chart import modal_chart
from dashboard.components.left_drawer.components.controls import setting_controls
from dashboard.components.left_drawer.components.date_time_section import date_time_section
from dashboard.components.left_drawer.components.tag_filter import tag_filter
from dashboard.components.left_drawer.components.type_filter import brick_type_filter
from dashboard.config.id_config import *

header = dmc.Center(dmc.Text("Mitwelten Discover", size="lg"))


def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md")


def settings(node_types, tags_data, depl_colors):
    return dmc.Container(
        children=[
            header,
            dmc.Space(h=30),
            dmc.ScrollArea([
                html.Div([
                    divider("Time Range Selection"),
                    date_time_section(),

                    divider("Filter"),
                    brick_type_filter(node_types, depl_colors),
                    tag_filter(tags_data),
                    dmc.Space(h=30),

                    divider("Settings"),
                    setting_controls(),
                ],
                    id=ID_LEFT_DRAWER_CONTENT_SCROLL_AREA,
                ),
            ],
                offsetScrollbars=True,
                type="always"
            ),
            modal_chart,
        ],
        fluid=True,
        style={"height": "100vh"}
    ),


@callback(
    Output(ID_MAP_LAYER_GROUP, "children"),
    Output(ID_DATE_RANGE_PICKER, "value"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_TAG_CHIPS_GROUP, "value"),
    Input(ID_DEPLOYMENT_DATA_STORE, "data"),
    Input(ID_DATE_RANGE_PICKER, "value"),
    Input(ID_DATE_RANGE_SEGMENT, "value"),
    Input(ID_DEPLOYMENT_COLOR_STORE, "data"),
)
def filter_map_data(checkboxes, chips, deployment_data, time_range, seg_time_range, colors):
    trigger_id = dash.ctx.triggered_id
    checkboxes = list(filter(lambda c: c != "all", checkboxes))
    print(seg_time_range)

    if not seg_time_range:
        seg_time_range = 7
    else:
        seg_time_range = int(seg_time_range)

    update_picker = [
        datetime.strptime(time_range[0], "%Y-%m-%d").date(),
        datetime.strptime(time_range[1], "%Y-%m-%d").date()
    ]
    if trigger_id == ID_DATE_RANGE_SEGMENT:
        update_picker = [datetime.now().date() - timedelta(weeks=seg_time_range), datetime.now().date()]

    depl_to_show = {}

    # parse to json objects
    for key in deployment_data:
        deployment_data[key] = map(lambda d: json.loads(d), deployment_data[key])

    # checkbox filter
    for active in checkboxes:
        # depl_to_show => {"key": [Deployments]
        depl_to_show[active] = deployment_data[active]

    # chip filter
    if chips:
        for key in depl_to_show.keys():
            depl_to_show[key] = filter(lambda d: any(item in chips for item in d["tags"]), depl_to_show[key])

    def was_deployed(depl):
        selected_start = update_picker[0]
        selected_end = update_picker[1]

        node_start = depl["period_start"]
        node_end = depl["period_end"]

        if node_start is not None:
            node_start = datetime.strptime(node_start[0:10], "%Y-%m-%d").date()
            start_in_period = selected_start <= node_start <= selected_end
            if start_in_period:
                return True
            if node_end is not None:
                node_end = datetime.strptime(node_end[0:10], "%Y-%m-%d").date()
                end_in_period = selected_start <= node_end <= selected_end
                if end_in_period:
                    return True
                return node_start < selected_start and node_end > selected_end
            else:
                return node_start <= selected_end

    # time filter
    for key in depl_to_show.keys():
        depl_to_show[key] = filter(was_deployed, depl_to_show[key])

    markers = []

    for key in depl_to_show.keys():
        for d in depl_to_show[key]:
            markers.append(dl.DivMarker(
                children=[
                    DashIconify(
                        icon="ion:location-sharp",
                        height=24,
                        color=f"{colors[d['node_type']]}"
                    ),
                    dl.Tooltip(f"{d['node_type']}\n{d['node_label']}"),
                ],
                iconOptions=dict(className="div-icon", iconAnchor=[32, 16]),
                position=[d["lat"], d["lon"]],
                id={"role": f"{d['node_type']}", "id": d['deployment_id'], "label": d["node_label"]},
            ))

    return markers, update_picker
