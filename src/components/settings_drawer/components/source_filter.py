from functools import reduce

import dash_mantine_components as dmc
from dash import dash, html, dcc, Output, Input

from src.config.id_config import *
from src.config.map_config import SOURCE_PROPS, get_source_props
from src.main import app
from src.util.decorators import spaced_section


def get_checkbox_by_type(node_type: str):
    return dmc.Checkbox(
        label=dmc.Group([
            dmc.Image(
                src=get_source_props(node_type)["marker"],
                width="24px",
                ),
            node_type,
        ]),
        value=node_type,
        size="xs",
        persistence=True,
    )


@spaced_section
def source_filter(args):
    source_types = reduce(
        list.__add__,
        [list(map(lambda x: get_checkbox_by_type(x),  SOURCE_PROPS.keys()))],
        [dmc.Checkbox(label="All", value="all", size="xs")]
    )

    return html.Div([
        dcc.Interval(id="remove-highlight", interval=3000, disabled=True),
        dcc.Store(id=ID_ALL_ACTIVE_STORE, data={"active": False}),
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

