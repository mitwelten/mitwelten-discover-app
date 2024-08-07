import re

import dash
import dash_mantine_components as dmc
from dash import html, Input, Output, State, no_update, ctx, ALL
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from urllib import parse 

from src.data.init import init_tags
from src.util.decorators import spaced_section
from src.config.app_config import PRIMARY_COLOR
from src.config.id_config import *
from src.main import app
from src.url.parse import update_query_data
from src.model.deployment import Deployment

fs_desc = dmc.Stack([
    dmc.Text("Field Study 1: Merian Gärten",   size="sm"),
    dmc.Text("Field Study 2: Dreispitz",       size="sm"),
    dmc.Text("Field Study 3: Reinacher Heide", size="sm"),
], spacing="sm")


@spaced_section
def tag_filter(args):
    all_tags  = init_tags()
    all_tags = [tag["name"] for tag in all_tags]

    predicate = re.compile("FS\d")

    fs_tags = []
    for tag in all_tags:
        if predicate.match(tag):
            fs_tags.append(tag)
    fs_tags = list(sorted(fs_tags))
    fs_tags.insert(0, "ANY")
    fs_value = args.get("fs")

    tags = sorted([t for t in all_tags if t not in fs_tags])
    tags_value = args.get("tags")

    if tags_value is not None:
        tags_value = tags_value.split("+")
        tags_value = [x.replace("_", " ") for x in tags_value]
    else:
        tags_value = []

    return html.Div([
        dmc.Text("Field Study", size="sm"),
        dmc.Space(h=10),
        dmc.Center(
            dmc.HoverCard(
                position="top",
                withArrow=True,
                width="240px",
                shadow="lg",
                style={"display": "flex", "alignItems":"center"},
                children=[
                    dmc.HoverCardTarget(
                        children=
                        dmc.Center([
                            dmc.SegmentedControl(
                                color=PRIMARY_COLOR,
                                id=ID_FS_TAG_CHIPS_GROUP,
                                data=fs_tags,
                                value=fs_value,
                                size="xs"
                                ),
                            ]),
                        #dmc.ThemeIcon(
                            #    size="sm",
                            #    variant="filled",
                            #    radius="sm",
                            #    color=PRIMARY_COLOR, 
                            #    children=DashIconify(icon="material-symbols:info-i-rounded", width=16),
                            #    style={"cursor": "pointer"}
                            #),
                        ),
                    dmc.HoverCardDropdown(children=fs_desc)
                    ],
                ),
            ),

        dmc.Space(h=20),
        dmc.Group([
            dmc.Text("Additional Tags",
                     size="sm",
                     style={"display": "inline-block"}
                     ),
            dmc.Group([
                dmc.ActionIcon(
                    DashIconify(
                        icon="material-symbols:add",
                        ),
                    variant="filled",
                    id=ID_OPEN_CHIP_MODAL_BUTTON,
                    size="sm",
                    color=PRIMARY_COLOR,
                    n_clicks=0,
                    radius="sm",
                    ),
                dmc.Button(
                    "Clear",
                    variant="light",
                    color=PRIMARY_COLOR,
                    compact=True,
                    size="xs",
                    radius="xl",
                    id=ID_TAG_RESET_BUTTON,
                    ),
                ]),
            ],
                  position="apart"
                  ),
        dmc.Space(h=10),
        dmc.Center([
            dmc.ChipGroup(
                [dmc.Chip(x, value=x, size="xs") for x in tags_value],
                id=ID_TAG_CHIPS_GROUP,
                value=tags_value,
                multiple=True
                ),
            html.Div(
                dmc.Modal(
                    title="Select Tags",
                    id=ID_CHIPS_MODAL,
                    zIndex=1000000,
                    children=[
                        dmc.ChipGroup(
                            children=[dmc.Chip(x, value=x, size="xs") for x in tags],
                            id=ID_MODAL_CHIPS_GROUP,
                            value=tags_value,
                            multiple=True
                            ),
                        dmc.Space(h=20),
                        dmc.Center(dmc.Button("Ok", id=ID_CLOSE_CHIP_MODAL_BUTTON)),
                        ],
                    ),
                ),
            ])])


@app.callback(
    Output(ID_TAG_CHIPS_GROUP, "children", allow_duplicate=True),
    Output(ID_TAG_CHIPS_GROUP, "value", allow_duplicate=True),
    Output(ID_MODAL_CHIPS_GROUP, "value"),
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_TAG_RESET_BUTTON, "n_clicks"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True
)
def reset_tags(_, data):
    return [], [], [], update_query_data(data, {"tags": None})


@app.callback(
    Output(ID_CHIPS_MODAL, "opened"),
    Output(ID_TAG_CHIPS_GROUP, "children", allow_duplicate=True),
    Output(ID_TAG_CHIPS_GROUP, "value", allow_duplicate=True),
    Input(ID_OPEN_CHIP_MODAL_BUTTON, "n_clicks"),
    Input(ID_CLOSE_CHIP_MODAL_BUTTON, "n_clicks"),
    Input(ID_MODAL_CHIPS_GROUP, "value"),
    Input(ID_TAG_CHIPS_GROUP, "value"),
    Input(ID_TAG_CHIPS_GROUP, "children"),
    State(ID_CHIPS_MODAL, "opened"),
    prevent_initial_call=True,
)
def select_tags(_1, _2, modal_value, active_chips, children, opened):
    current_chips = list(map(lambda x: x["props"]["value"], children))
    filtered = list(filter(lambda d: d not in active_chips, current_chips))
    new_active_chips = list(filter(lambda x: x not in filtered, modal_value))

    new_children = [dmc.Chip(x, value=x, size="xs") for x in modal_value]
    trigger_id = dash.ctx.triggered_id
    if trigger_id == ID_CLOSE_CHIP_MODAL_BUTTON or trigger_id == ID_OPEN_CHIP_MODAL_BUTTON:
        return not opened, new_children, new_active_chips
    return opened, children, active_chips


@app.callback(
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_FS_TAG_CHIPS_GROUP, "value"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
)
def update_fs_tag_in_url_params(value, data):
    return update_query_data(data, {"fs": value})

@app.callback(
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_TAG_CHIPS_GROUP, "value"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
)
def update_tag_in_url_params(value, data):
    value = "+".join(value)
    value = value.replace(" ", "_")
    return update_query_data(data, {"tags": value})


@app.callback(
    Output(ID_MAP, "viewport", allow_duplicate=True),
    Input(ID_FS_TAG_CHIPS_GROUP, "value"),
    Input({"role": ALL, "label": "Store", "type": "physical"}, "data"),
    State(ID_MAP, "bounds"),
    prevent_initial_call=True
)
def move_map_to_fs_area(fs_tag, sources, bounds):
    new_bounds = bounds if bounds is not None else [[None, None],[None, None]]
    deployment_data = {}
    for source in sources:
        deployment_data[source["type"]] = source["entries"]

    top     = None
    bottom  = None
    left    = None
    right   = None

    for key in deployment_data.keys():
        for d in deployment_data[key]:
            d = Deployment(d)
            if fs_tag in d.tags or fs_tag == "ANY":
                if left is None or left > d.lon: 
                    left = d.lon

                if right is None or right < d.lon :
                    right = d.lon

                if bottom is None or bottom > d.lat: 
                    bottom = d.lat

                if top is None or top < d.lat: 
                    top = d.lat

    new_bounds[1][0] = top
    new_bounds[0][0] = bottom 
    new_bounds[0][1] = left   
    new_bounds[1][1] = right 

    return dict(bounds=bounds, transition="flyTo")
