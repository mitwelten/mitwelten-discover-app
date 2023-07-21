import json
from datetime import datetime, date, timedelta
from functools import reduce

import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, callback, State, dcc, ALL
from dash_iconify import DashIconify

from dashboard.config import api_config as api


def settings(deployment_data, tags_data):
    return dmc.Container(
        children=[
            dmc.Center(dmc.Text("Mitwelten Discover", size="lg")),
            dmc.Space(h=30),
            dmc.Divider(label="Time Range Selection", labelPosition="center", size="md"),
            dmc.Space(h=10),
            dmc.SegmentedControl(
                id="segmented-time-range",
                color="green",
                value="1",
                fullWidth=True,
                data=[
                    {"value": "100000", "label": "All"},
                    {"value": "52", "label": "12 M"},
                    {"value": "26", "label": "6 M"},
                    {"value": "12", "label": "3 M"},
                    {"value": "4", "label": "1 M"},
                    {"value": "1", "label": "1 W"},
                ],
                mt=10,
            ),
            dmc.Space(h=20),
            dmc.Center(
                dmc.DateRangePicker(
                    id="date-range-picker",
                    label="Date Range",
                    inputFormat="DD MMMM, YY",
                    description="",
                    minDate=date(2020, 8, 5),
                    value=[datetime.now().date() - timedelta(days=7), datetime.now().date()],
                    style={"width": 250},
                ),
            ),
            dmc.Space(h=10),
            dmc.Center(dmc.Text(id="selected-date-date-range-picker", size="xs")),

            dmc.Space(h=30),
            dmc.Divider(label="Settings", labelPosition="center", size="md"),

            dmc.Space(h=10),
            dcc.Store(id="checkbox-all", data={"active": False}),
            dmc.CheckboxGroup(
                id="checkbox-group",
                label="Bricks",
                description="Select the displayed Bricks",
                orientation="vertical",
                withAsterisk=False,
                offset="xs",
                children=reduce(
                    list.__add__,
                    [list(map(lambda x: dmc.Checkbox(label=x, value=x, size="xs"), sorted(deployment_data.keys())))],
                    [dmc.Checkbox(label="All", value="all", size="xs")]),
                value=[],
            ),
            dmc.Text(id="checkbox-group-output"),
            dmc.Space(h=30),

            dmc.Text("Select the displayed TAG's", size="xs", color="gray"),
            dmc.Space(h=10),
            dmc.Center([
                dmc.ChipGroup(
                    [dmc.Chip(x, value=x, size="xs") for x in tags_data],
                    multiple=True,
                    value=[],
                    id="chips-group",
                ),
            ]),
            html.Div(
                dmc.Switch(
                    offLabel=DashIconify(icon="radix-icons:moon", width=16),
                    onLabel=DashIconify(icon="radix-icons:sun", width=16),
                    size="xs",
                    id="theme-switch"
                ),
                id="theme-switch-container"
            )
        ],
        fluid=True,
        style={"height": "100vh"}
    )


@callback(
    [
        Output("checkbox-group", "value"),
        Output("checkbox-all", "data"),
    ],
    [
        Input("checkbox-group", "value"),
        Input("checkbox-group", "children"),
        Input("checkbox-all", "data"),
    ]
)
def activate_all(value, data, all_enabled):
    values = list(map(lambda x: x["props"]["value"], data))

    if "all" in value and not all_enabled["active"]:
        return values, {"active": True}
    if "all" not in value and all_enabled["active"] and len(value) == len(values) - 1:
        return [], {"active": False}
    if all_enabled["active"]:
        return list(filter(lambda x: x != "all", value)), {"active": False}


@callback(
    [
        Output("data_layer", "children"),
        Output("date-range-picker", "value"),
    ],
    [
        Input("checkbox-group", "value"),
        Input("chips-group", "value"),
        Input("deployment_data", "data"),
        Input("date-range-picker", "value"),
        Input("segmented-time-range", "value"),
    ]
)
def checkbox(checkboxes, chips, deployment_data, time_range, seg_time_range):
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
                children=dl.Tooltip(d["node_label"]),
                id={"role": f"marker-{d['node_type']}", "id": d['node_label']},
                icon=dict(iconUrl=api.URL_ICON, iconAnchor=[32, 16]),
            ))

    return markers, update_picker


@callback(
    Output("theme-switch-container", "children"),
    Input({"role": "marker-Pax Counter", "id": ALL}, "n_clicks")
)
def marker_click(click):
    print(f"{click} from {dash.ctx.triggered_id}")
    return dash.no_update


@callback(
    Output('app-theme', 'theme'),
    Input('app-theme', 'theme'),
    Input("theme-switch", "checked"),
    prevent_intial_call=True)
def switch_theme(theme, checked):
    if not checked:
        theme.update({'colorScheme': 'light'})
    else:
        theme.update({'colorScheme': 'dark'})
    return theme
