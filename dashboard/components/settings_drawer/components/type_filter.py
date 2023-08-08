from functools import reduce

import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, dcc, Output, Input, State
from dash_iconify import DashIconify

from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.util.decorators import spaced_section


def get_checkbox_by_type(node_type: str, colors: dict):
    return dmc.Checkbox(
        label=dmc.Group([
            html.Div(
                className="color-point",
                style={"background": f"{colors[node_type]['color']}"}
            ),
            node_type,
        ]),
        value=node_type,
        size="xs",
        persistence=True,
    )


@spaced_section
def type_filter(data, colors):
    brick_types = reduce(
        list.__add__,
        [list(map(lambda x: get_checkbox_by_type(x, colors), (sorted(data.keys()))))],
        [dmc.Checkbox(label="All", value="all", size="xs")])

    deployment_ids = []
    for key in data.keys():
        for entry in data[key]:
            deployment_ids.append(dict(label=f"{key} - {entry['deployment_id']}", value=entry))

    return html.Div([
        dcc.Interval(id="remove-highlight", interval=3000, disabled=True),
        dcc.Store(id=ID_ALL_ACTIVE_STORE, data={"active": False}),
        dmc.Group([
            dmc.Select(
                id=ID_DEPLOYMENT_SELECT,
                data=deployment_ids,
                placeholder="Deployment ID",
                searchable=True,
                nothingFound="ID not found",
                style={"width": "100%"},
                size="sm",
                icon=DashIconify(icon="material-symbols:search", width=20),
                rightSection=dmc.ActionIcon(
                    DashIconify(icon="material-symbols:my-location", width=20),
                    size="lg",
                    variant="subtle",
                    id=ID_SEARCH_DEPLOYMENT_BUTTON,
                    n_clicks=0,
                    color="mitwelten_green",
                ),
            ),
        ],
            position="apart",
        ),
        dmc.CheckboxGroup(
            id=ID_TYPE_CHECKBOX_GROUP,
            orientation="vertical",
            withAsterisk=False,
            offset="xs",
            children=brick_types,
            value=["all"],
        ),
    ])


@app.callback(
    Output(ID_TYPE_CHECKBOX_GROUP, "value"),
    Output(ID_ALL_ACTIVE_STORE, "data"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    Input(ID_TYPE_CHECKBOX_GROUP, "children"),
    Input(ID_ALL_ACTIVE_STORE, "data"),
)
def activate_all(value, data, all_enabled):
    values = list(map(lambda x: x["props"]["value"], data))

    if "all" in value and not all_enabled["active"]:
        return values, {"active": True}

    if "all" not in value and all_enabled["active"] and len(value) == len(values) - 1:
        return [], {"active": False}

    if all_enabled["active"]:
        return list(filter(lambda x: x != "all", value)), {"active": False}

    return dash.no_update


@app.callback(
    Output(ID_MAP, "useFlyTo", allow_duplicate=True),
    Output(ID_MAP, "center", allow_duplicate=True),
    Output(ID_MAP, "zoom", allow_duplicate=True),
    Output("remove-highlight", "disabled", allow_duplicate=True),
    Output(ID_HIGHLIGHT_LAYER_GROUP, "children", allow_duplicate=True),
    Input(ID_SEARCH_DEPLOYMENT_BUTTON, "n_clicks"),
    State(ID_DEPLOYMENT_SELECT, "value"),
    prevent_initial_call=True
)
def search_deployment(_, value):
    if value is not None:
        lat = value["location"]["lat"]
        lon = value["location"]["lon"]
        marker = dl.Marker(
            position=[lat, lon],
            icon=dict(iconUrl=f"assets/markers/highlight-circle.svg", iconAnchor=[40, 30], iconSize=80)
        )
        return True, (lat, lon), 20, False, [marker]
    else:
        return dash.no_update


@app.callback(
    Output(ID_HIGHLIGHT_LAYER_GROUP, "children", allow_duplicate=True),
    Output(ID_MAP, "useFlyTo", allow_duplicate=True),
    Output("remove-highlight", "disabled", allow_duplicate=True),
    Input("remove-highlight", "n_intervals"),
    prevent_initial_call=True
)
def remove_highlight(_):
    return [], False, True
