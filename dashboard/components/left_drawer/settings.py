import json

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, callback, ALL, State, dcc

from dashboard.components.left_drawer.components.brick_type_filter import brick_type_filter
from dashboard.components.left_drawer.components.date_time_section import date_time_section
from dashboard.components.left_drawer.components.setting_controls import setting_controls
from dashboard.components.left_drawer.components.tag_filter import tag_filter
from dashboard.config import api_config as api
from dashboard.api.api_client import get_env_tod
from dashboard.config.id_config import \
    ID_MARKER_CLICK_STORE, \
    ID_CHART_MODAL, \
    ID_MEASUREMENT_CHART, \
    ID_LEFT_DRAWER_CONTENT_SCROLL_AREA, ID_MAP_LAYER_GROUP, ID_DATE_RANGE_PICKER, ID_TYPE_CHECKBOX_GROUP, \
    ID_TAG_CHIPS_GROUP, ID_DATE_RANGE_SEGMENT, ID_DEPLOYMENT_DATA_STORE

from util.functions import safe_reduce

header = dmc.Center(dmc.Text("Mitwelten Discover", size="lg"))
fig = px.line()


def settings(brick_types, tags_data):
    return dmc.Container(
        children=[
            dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(env=None)),
            html.Div([
                dmc.Modal(
                    title="Measurement Chart",
                    id=ID_CHART_MODAL,
                    centered=True,
                    zIndex=10000,
                    size="80%",
                    closeOnClickOutside=True,
                    closeOnEscape=False,
                    children=[
                        dmc.Container(
                            dcc.Graph(
                                id=ID_MEASUREMENT_CHART,
                                figure=fig,
                                config={"displayModeBar": False},
                                style={"height": "inherit", "width": "inherit"}
                            ),
                        )
                    ],
                ),
            ]
            ),
            header,
            dmc.Space(h=30),
            dmc.ScrollArea([
                html.Div([
                    dmc.Divider(label="Time Range Selection", labelPosition="center", size="md"),
                    date_time_section(),

                    dmc.Divider(label="Filter", labelPosition="center", size="md"),
                    brick_type_filter(brick_types),
                    tag_filter(tags_data),
                    dmc.Space(h=30),

                    dmc.Divider(label="Settings", labelPosition="center", size="md"),
                    setting_controls(),
                ],
                    id=ID_LEFT_DRAWER_CONTENT_SCROLL_AREA,
                ),
            ],
                offsetScrollbars=True,
                type="always"
            ),
        ],
        fluid=True,
        style={"height": "100vh"}
    ),


@callback(
    [
        Output(ID_MAP_LAYER_GROUP, "children"),
        Output(ID_DATE_RANGE_PICKER, "value"),
    ],
    [
        Input(ID_TYPE_CHECKBOX_GROUP, "value"),
        Input(ID_TAG_CHIPS_GROUP, "value"),
        Input(ID_DEPLOYMENT_DATA_STORE, "data"),
        Input(ID_DATE_RANGE_PICKER, "value"),
        Input(ID_DATE_RANGE_SEGMENT, "value"),
    ]
)
def filter_map_data(checkboxes, chips, deployment_data, time_range, seg_time_range):
    trigger_id = dash.ctx.triggered_id
    checkboxes = list(filter(lambda c: c != "all", checkboxes))

    if not seg_time_range:
        seg_time_range = 7
    else:
        seg_time_range = int(seg_time_range)

    update_picker = [
        datetime.strptime(time_range[0], "%Y-%m-%d").date(),
        datetime.strptime(time_range[1], "%Y-%m-%d").date()
    ]
    if trigger_id == "segmented-time-range":
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
            markers.append(dl.Marker(
                position=[d["lat"], d["lon"]],
                children=dl.Tooltip(f"{d['node_type']}\n{d['node_label']}"),
                id={"role": f"{d['node_type']}", "id": d['deployment_id'], "label": d["node_label"]},
                icon=dict(iconUrl=api.URL_ICON, iconAnchor=[32, 16]),
            ))

    return markers, update_picker


@callback(
    Output(ID_MEASUREMENT_CHART, "figure"),
    Output(ID_CHART_MODAL, "opened"),
    Output(ID_MARKER_CLICK_STORE, "data"),
    Input({"role": "Env. Sensor", "id": ALL, "label": ALL}, "n_clicks"),
    Input("date-range-picker", "value"),
    Input(ID_MARKER_CLICK_STORE, "data"),
    State(ID_CHART_MODAL, "opened"),
    prevent_initial_call=True,
)
def marker_click(n_clicks, date, data, opened):
    click_sum = safe_reduce(lambda x, y: x + y, n_clicks)
    print(n_clicks, date, data, opened, dash.ctx.triggered_id)

    has_click_triggered = click_sum != data["env"]

    if click_sum is not None:
        data["env"] = click_sum

    if has_click_triggered and dash.ctx.triggered_id is not None:
        trigger_id = dash.ctx.triggered_id["id"]
        print(dash.ctx.triggered_id, opened)
        resp = get_env_tod(trigger_id, "temperature", "mean", "1h")
        resp["time"] = pd.to_datetime(resp["time"], format="%Y-%m-%d", exact=False)
        new_figure = px.line(
            resp,
            x='time',
            y="value",
            title=f"{dash.ctx.triggered_id['role']} - {dash.ctx.triggered_id['label']}",
        )
        return new_figure, True, data
    return dash.no_update
