from functools import reduce

import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input

from dashboard.components.left_drawer.components.decorators import spaced_section
from dashboard.config.id_config import ID_ALL_ACTIVE_STORE, ID_TYPE_CHECKBOX_GROUP


@spaced_section
def brick_type_filter(data):
    brick_types = reduce(
        list.__add__,
        [list(map(lambda x: dmc.Checkbox(label=x, value=x, size="xs"), sorted(data.keys())))],
        [dmc.Checkbox(label="All", value="all", size="xs")])

    return html.Div([
        dcc.Store(id=ID_ALL_ACTIVE_STORE, data={"active": False}),
        dmc.CheckboxGroup(
            id=ID_TYPE_CHECKBOX_GROUP,
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
        Output(ID_TYPE_CHECKBOX_GROUP, "value"),
        Output(ID_ALL_ACTIVE_STORE, "data"),
    ],
    [
        Input(ID_TYPE_CHECKBOX_GROUP, "value"),
        Input(ID_TYPE_CHECKBOX_GROUP, "children"),
        Input(ID_ALL_ACTIVE_STORE, "data"),
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
