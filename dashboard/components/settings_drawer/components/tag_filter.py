import json
import re

import dash
from dash import dcc
import dash_mantine_components as dmc
from dash import html, Input, Output, State
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.config.id import *
from dashboard.maindash import app


def tag_filter(all_tags):
    all_tags = json.loads(all_tags)
    p = re.compile("FS\d")
    fs_tags = [s for s in all_tags if p.match(s)]
    tags = [t for t in all_tags if t not in fs_tags]
    return html.Div([
        dcc.Store(id=ID_CURRENT_TAG_DATA_STORE, data=[]),
        dmc.Text("Field Study",
                 size="sm",
                 color="dimmed",
                 ),
        dmc.Center([
            dmc.SegmentedControl(
                color=PRIMARY_COLOR,
                id=ID_FS_TAG_CHIPS_GROUP,
                data=fs_tags,
                value="FS1",
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
                            [dmc.Chip(x, value=x, size="xs", styles={"iconWrapper": {"className": ""}}) for x in sorted(tags)],
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
    Output(ID_TAG_CHIPS_GROUP, "children", allow_duplicate=True),
    Output(ID_TAG_CHIPS_GROUP, "value", allow_duplicate=True),
    Output(ID_MODAL_CHIPS_GROUP, "value"),
    Input(ID_TAG_RESET_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def reset_tags(_):
    return [], [], []


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
