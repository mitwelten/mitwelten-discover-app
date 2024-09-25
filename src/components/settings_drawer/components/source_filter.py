import dash_mantine_components as dmc
from dash import html, Output, Input, State, ctx, no_update

from src.model.url_parameter import UrlParameter
from src.config.id_config import *
from src.config.map_config import SOURCE_PROPS, get_source_props
from src.main import app
from src.url.parse import update_query_data


def get_checkbox_by_type(node_type: str):
    return dmc.Checkbox(
        label=dmc.Group([
            html.Div(
                className="color-point",
                style={"background": get_source_props(node_type)["color"]}
            ),
            dmc.Text(get_source_props(node_type)["name"]),
        ]),
        value=node_type,
    )


def source_filter(params: UrlParameter):

    active = list(SOURCE_PROPS.keys()) if params.devices is None else params.devices
    source_types = [get_checkbox_by_type(x) for x in  SOURCE_PROPS.keys()]

    return html.Div([
        dmc.Checkbox(
            id=ID_ALL_CHECKBOX,
            label="All", 
            checked=len(active) == len(SOURCE_PROPS.keys()),
            value="all", 
            size="sm",
            ),
        dmc.Space(h=20),
            dmc.CheckboxGroup(
                id=ID_TYPE_CHECKBOX_GROUP,
                withAsterisk=False,
                children=dmc.Stack(source_types),
                value=active,
                ),
            ],
    )

@app.callback(
        Output(ID_TYPE_CHECKBOX_GROUP, "value"),
        Output(ID_ALL_CHECKBOX, "checked"),
        Input(ID_ALL_CHECKBOX, "checked"),
        Input(ID_TYPE_CHECKBOX_GROUP, "value"),
        prevent_initial_call=True,
)
def activate_all(all, values):
    if ctx.triggered_id == ID_ALL_CHECKBOX:
        if all:
            return list(SOURCE_PROPS.keys()), no_update
        return [], no_update
    else:
        if len(values) == len(SOURCE_PROPS.keys()):
            return values, True
        else :
            return values, False




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
