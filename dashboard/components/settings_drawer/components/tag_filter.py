import json
import re
from pprint import pprint

import dash
from dash import dcc
import dash_mantine_components as dmc
from dash import html, Input, Output, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.config.id_config import *
from dashboard.maindash import app
from dashboard.model.tag import Tag


def tag_filter():
    return html.Div([
        dmc.Text("Field Study",
                 color="dimmed",
                 size="sm",
                 ),
        dmc.Center([
            dmc.SegmentedControl(
                color=PRIMARY_COLOR,
                id=ID_FS_TAG_CHIPS_GROUP,
                data=[],
                persistence=True,
            ),
        ]),
        dmc.Space(h=20),
        dmc.Group([
            dmc.Text("Additional Tags",
                     size="sm",
                     color="dimmed",
                     style={"display": "inline-block"}
                     ),
            dmc.Group([
                dmc.ActionIcon(
                    DashIconify(
                        icon="material-symbols:add",
                        color=PRIMARY_COLOR,
                    ),
                    variant="light",
                    id=ID_OPEN_CHIP_MODAL_BUTTON,
                    size="md",
                    n_clicks=0,
                    radius="xl",
                ),
                dmc.Button(
                    "Clear",
                    variant="light",
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
                [dmc.Chip(x, value=x, size="xs") for x in []],
                id=ID_TAG_CHIPS_GROUP,
                value=[],
                multiple=True
            ),
            html.Div(
                dmc.Modal(
                    title="Select Tags",
                    id=ID_CHIPS_MODAL,
                    zIndex=10000,
                    children=[
                        dmc.ChipGroup(
                            id=ID_MODAL_CHIPS_GROUP,
                            value=[],
                            multiple=True
                        ),
                        dmc.Space(h=20),
                        dmc.Center(dmc.Button("Ok", id=ID_CLOSE_CHIP_MODAL_BUTTON)),
                    ],
                ),
            ),
        ]),
    ])


@app.callback(
    Output(ID_FS_TAG_CHIPS_GROUP, "data"),
    Output(ID_FS_TAG_CHIPS_GROUP, "value"),
    Output(ID_MODAL_CHIPS_GROUP, "children"),
    Input(ID_TAG_DATA_STORE, "data"),
    State(ID_FS_TAG_CHIPS_GROUP, "value"),
    prevent_initial_call=True
)
def update_fs_tags_from_store(all_tags, active_tag):
    if all_tags is None:
        raise PreventUpdate
    predicate = re.compile("FS\d")

    fs_tags   = list(sorted(([tag["name"] for tag in all_tags if predicate.match(tag["name"])])))
    value     = active_tag if active_tag is not None else fs_tags[0]

    tags      = [t["name"] for t in all_tags if t["name"] not in fs_tags]
    chips     = [dmc.Chip(x, value=x, size="xs", styles={"iconWrapper": {"className": ""}}) for x in sorted(tags)],
    return fs_tags, value, *chips


@app.callback(
    Output(ID_TAG_CHIPS_GROUP, "children", allow_duplicate=True),
    Output(ID_TAG_CHIPS_GROUP, "value", allow_duplicate=True),
    Output(ID_MODAL_CHIPS_GROUP, "value"),
    Input(ID_TAG_RESET_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def reset_tags(_):
    # TODO: fix bug marker still be visible after clearing additional tags
    return [], [], []


# TODO: refactor
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
