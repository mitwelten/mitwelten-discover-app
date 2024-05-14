from functools import reduce

import dash_mantine_components as dmc
from dash import dash, html, dcc, Output, Input, State

from src.config.id_config import *
from src.config.map_config import SOURCE_PROPS, get_source_props
from src.main import app
from src.util.decorators import spaced_section
from src.util.util import update_query_data


def get_checkbox_by_type(node_type: str):
    return dmc.Checkbox(
        label=dmc.Group([
            html.Div(
                className="color-point",
                style={"background": get_source_props(node_type)["color"]}
            ),
            #dmc.Image(
            #    src=get_source_props(node_type)["marker"],
            #    width="24px",
            #    ),
            get_source_props(node_type)["name"],
        ]),
        value=node_type,
        size="xs",
        persistence=True,
        color="#003399"
    )


@spaced_section
def source_filter(args):

    active = args.get("devices", ["all"])
    if active[0] != "all":
        active = active.split(",")
        active = [x.replace("_", " ") for x in active]

    source_types = reduce(
        list.__add__,
        [list(map(lambda x: get_checkbox_by_type(x),  SOURCE_PROPS.keys()))],
        [dmc.Checkbox(label=dmc.Group(["All"]), value="all", size="xs")] # dmc.Space(w=4) before "All"
    )

    return html.Div([
        dcc.Store(id=ID_ALL_ACTIVE_STORE, data={"active": False}),
        dmc.CheckboxGroup(
            id=ID_TYPE_CHECKBOX_GROUP,
            orientation="vertical",
            withAsterisk=False,
            offset="xs",
            children=source_types,
            value=active,
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
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
)
def update_tag_in_url_params(value, data):
    if "all" in value:
        value = "all"
    else:
        value = [x.replace(" ", "_") for x in value if x != "all"]

    return update_query_data(data, {"devices": value})
