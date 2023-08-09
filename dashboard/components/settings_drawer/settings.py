from datetime import datetime

import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, State

from dashboard.components.settings_drawer.components.date_time_section import date_time_section
from dashboard.components.settings_drawer.components.environment_filter import environment_filter
from dashboard.components.settings_drawer.components.general_controls import general_controls
from dashboard.components.settings_drawer.components.tag_filter import tag_filter
from dashboard.components.settings_drawer.components.type_filter import type_filter
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.deployment import Deployment
from util.functions import was_deployed


def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md")


def settings_content(node_types, tags_data, depl_colors):
    return dmc.Container(
        children=[
            dmc.Space(h=30),
            html.Div([
                divider("Date Range"),
                date_time_section(),
                divider("Data Source"),
                type_filter(node_types, depl_colors),
                divider("Tags"),
                tag_filter(tags_data),
                divider("Environment"),
                environment_filter(),
                divider("Settings"),
                general_controls(),
            ],
                id=ID_LEFT_DRAWER_CONTENT_SCROLL_AREA,
                style={"height": "100%"}
            )],
        fluid=True,
        style={"height": "calc(100vh - 100px)"},
        className="scroll-area"
    )


def marker_popup(deployment, color):
    start = datetime.strftime(datetime.fromisoformat(deployment.period_start), '%d %b %Y - %H:%M')
    end = datetime.strftime(datetime.fromisoformat(deployment.period_start), '%d %b %Y - %H:%M') if deployment.period_end else "-"
    return dmc.Container([
        dmc.Group([
            dmc.Group([
                html.Div(
                    className="color-point",
                    style={"background": f"{color}"}
                ),
                dmc.Text(deployment.node_type, weight=700, size="sm"),
            ],
                position="left",
                spacing="sm"
            ),
            dmc.Text(deployment.node_label, size="sm"),
        ],
            position="apart"
        ),
        dmc.Space(h=10),
        dmc.Divider(),
        dmc.Space(h=10),
        dmc.Group([
            dmc.Text("Deployment ID", size="xs"),
            dmc.Text(
                deployment.deployment_id,
                size="xs",
                color="dimmed",
            ),
        ],
            position="apart"
        ),
        dmc.Group([
            dmc.Text("Start", size="xs"),
            dmc.Text(start, size="xs", color="dimmed"),
        ],
            position="apart"
        ),
        dmc.Group([
            dmc.Text("End", size="xs"),
            dmc.Text(end, size="xs", color="dimmed"),
        ],
            position="apart"
        ),
        dmc.Space(h=10),
        dmc.Group(
            children=[dmc.Badge(t, size="sm", variant="outline") for t in deployment.tags],
            spacing="xs"
        ),
    ],
        fluid=True,
        style={"width": "240px"}
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
def filter_map_data(checkboxes, tags, fs_tag, time_range, colors, deployment_data):
    checkboxes = list(filter(lambda c: c != "all", checkboxes))

    depl_to_show = {}

    # parse to json objects
    for key in deployment_data:
        deployment_data[key] = list(map(lambda depl: Deployment(depl), deployment_data[key]))

    # type filter
    for active in checkboxes:
        # depl_to_show:  {"key": [Deployments]
        depl_to_show[active] = deployment_data[active]

    if fs_tag != "All":
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
                    id={"role": f"{d.node_type}", "id": d.deployment_id, "label": d.node_label},
                )
            )
    return markers
