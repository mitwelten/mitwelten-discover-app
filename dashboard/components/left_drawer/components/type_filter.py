from functools import reduce

import dash
import dash_mantine_components as dmc
from dash import html, dcc, Output, Input

from dashboard.config.id_config import *
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

    return html.Div([
        dcc.Store(id=ID_ALL_ACTIVE_STORE, data={"active": False}),
        dmc.CheckboxGroup(
            id=ID_TYPE_CHECKBOX_GROUP,
            label="Devices",
            description="Select visible Bricks",
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
