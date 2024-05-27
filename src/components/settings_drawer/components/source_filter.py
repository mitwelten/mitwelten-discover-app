from functools import reduce

import dash_mantine_components as dmc
from dash import dash, html, dcc, Output, Input, State, ctx
from dash.exceptions import PreventUpdate

from src.config.id_config import *
from src.config.map_config import SOURCE_PROPS, get_source_props
from src.main import app
from src.util.decorators import spaced_section
from src.url.parse import update_query_data


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

    #active = list(SOURCE_PROPS.keys())
    active = args.get("devices")
    if active is not None:
        active = active.split(" ")
        active = [x.replace("_", " ") for x in active]
    else:
        active = list(SOURCE_PROPS.keys())

    source_types = [get_checkbox_by_type(x) for x in  SOURCE_PROPS.keys()]

    return html.Div([
        dmc.Checkbox(
            id="id-all-checkbox",
            label=dmc.Group(["All"]), 
            checked=True,
            value="all", 
            size="sm"
            ),
        dmc.Space(h=10),
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
        Input("id-all-checkbox", "checked"),
        prevent_initial_call=True,
)
def activate_all(value):
    if value:
        return list(SOURCE_PROPS.keys())
    return []



@app.callback(
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_TYPE_CHECKBOX_GROUP, "value"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
)
def update_tag_in_url_params(value, data):
    if len(value) == len(SOURCE_PROPS.keys()):
        value = None
    else:
        value = "+".join(value)
        value = value.replace(" ", "_")

    return update_query_data(data, {"devices": value})
