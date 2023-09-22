from functools import reduce
from pprint import pprint

import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, dcc, Output, Input, State, ALL
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.config.id_config import *
from dashboard.config.map_config import SOURCE_PROPS, get_source_props
from dashboard.maindash import app
from dashboard.util.decorators import spaced_section
from dashboard.util.util import get_identification_label


def get_checkbox_by_type(node_type: str):
    return dmc.Checkbox(
        label=dmc.Group([
            html.Div(
                className="color-point",
                style={"background": get_source_props(node_type)["color"]}
            ),
            node_type,
        ]),
        value=node_type,
        size="xs",
        persistence=True,
    )


@spaced_section
def source_filter(deployments):
    source_types = reduce(
        list.__add__,
        [list(map(lambda x: get_checkbox_by_type(x),  SOURCE_PROPS.keys()))],
        [dmc.Checkbox(label="All", value="all", size="xs")]
    )

    deployment_ids = []
    for key in deployments.keys():
        for entry in deployments[key]:
            deployment_ids.append(dict(label=f"{key} - {entry['node']['node_label']}", value=entry))

    return html.Div([
        dcc.Interval(id="remove-highlight", interval=3000, disabled=True),
        dcc.Store(id=ID_ALL_ACTIVE_STORE, data={"active": False}),
        dmc.Group([
            dmc.Select(
                id=ID_DEPLOYMENT_SELECT,
                data=deployment_ids,
                placeholder="Node Label",
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
                    color=PRIMARY_COLOR,
                ),
            ),
        ],
            position="apart",
        ),
        dmc.Space(h=10),
        dmc.CheckboxGroup(
            id=ID_TYPE_CHECKBOX_GROUP,
            orientation="vertical",
            withAsterisk=False,
            offset="xs",
            children=source_types,
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
        lat = value["entry"]["location"]["lat"]
        lon = value["entry"]["location"]["lon"]
        marker = dl.Marker(
            position=[lat, lon],
            icon=dict(iconUrl=f"assets/markers/highlight-circle.svg", iconAnchor=[40, 30], iconSize=80, className="blinking"),
        )
        return True, (lat, lon), 20, False, [marker]
    else:
        raise PreventUpdate


@app.callback(
    Output(ID_DEPLOYMENT_SELECT, "data"),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    State({"role": ALL, "label": "Store", "type": ALL}, "data"),
)
def update_search_data(active_types, _):
    new_data = []
    for source in dash.ctx.states_list[0]:
        if source["id"]["role"] in active_types:
            for entry in source["value"]["entries"]:
                label = get_identification_label(entry)
                new_data.append(
                    dict(
                        label=f"{source['id']['role']} - {label}",
                        value=dict(entry=entry, type=source['id']['role']))
                )
    return new_data


@app.callback(
    Output(ID_HIGHLIGHT_LAYER_GROUP, "children", allow_duplicate=True),
    Output(ID_MAP, "useFlyTo", allow_duplicate=True),
    Output("remove-highlight", "disabled", allow_duplicate=True),
    Input("remove-highlight", "n_intervals"),
    prevent_initial_call=True
)
def remove_highlight(_):
    return [], False, True
