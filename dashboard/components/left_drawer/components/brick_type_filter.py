from functools import reduce

import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input

from dashboard.components.left_drawer.components.decorators import spaced_section


@spaced_section
def brick_type_filter(data):
    brick_types = reduce(
        list.__add__,
        [list(map(lambda x: dmc.Checkbox(label=x, value=x, size="xs"), sorted(data.keys())))],
        [dmc.Checkbox(label="All", value="all", size="xs")])

    return html.Div([
        dcc.Store(id="checkbox-all", data={"active": False}),
        dmc.CheckboxGroup(
            id="checkbox-group",
            label="Bricks",
            description="Select visible Bricks",
            orientation="vertical",
            withAsterisk=False,
            offset="xs",
            children=brick_types,
            value=["all"],
        ),
    ])


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
