import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State
from dash_iconify import DashIconify
import dash_core_components as dcc

from dashboard.config import api_config as api
from dashboard.config.id_config import *


def tag_filter(data):
    return html.Div([
        dcc.Store(id=ID_CURRENT_TAG_DATA_STORE, data=api.DEFAULT_TAGS),
        dmc.Group([
            dmc.Text("Select visible TAG's",
                     size="xs",
                     color="dimmed",
                     style={"display": "inline-block"}
                     ),
            dmc.ActionIcon(
                DashIconify(
                    icon="material-symbols:add",
                    color=dmc.theme.DEFAULT_COLORS["green"][9],
                ),
                variant="outline",
                size="xs",
                id=ID_OPEN_MODAL_BUTTON,
                n_clicks=0,
                radius="xl",
            ),
        ],
            position="apart",
        ),
        dmc.Space(h=10),
        dmc.Center([
            dmc.ChipGroup(
                [dmc.Chip(x, value=x, size="xs") for x in api.DEFAULT_TAGS],
                multiple=True,
                id=ID_TAG_CHIPS_GROUP,
            ),
            html.Div(
                dmc.Modal(
                    title="Select Tag's",
                    id=ID_CHIPS_MODAL,
                    zIndex=10000,
                    overflow="inside",
                    children=[
                        dmc.ChipGroup(
                            [dmc.Chip(x, value=x, size="xs") for x in sorted(data)],
                            multiple=True,
                            id=ID_MODAL_CHIPS_GROUP,
                        ),
                        dmc.Space(h=20),
                        dmc.Center(dmc.Button("Add", id=ID_CLOSE_MODAL_BUTTON)),
                    ],
                ),
            ),
        ]),
    ])


@callback(
    Output(ID_CHIPS_MODAL, "opened"),
    Output(ID_TAG_CHIPS_GROUP, "children"),
    Output(ID_TAG_CHIPS_GROUP, "value"),
    Input(ID_OPEN_MODAL_BUTTON, "n_clicks"),
    Input(ID_CLOSE_MODAL_BUTTON, "n_clicks"),
    Input(ID_MODAL_CHIPS_GROUP, "value"),
    Input(ID_TAG_CHIPS_GROUP, "value"),
    Input(ID_TAG_CHIPS_GROUP, "children"),
    State(ID_CHIPS_MODAL, "opened"),
    prevent_initial_call=True,
)
def toggle_modal(_1, _2, value, active_chips, children, opened):
    new_children = [dmc.Chip(x, value=x, size="xs") for x in value]
    current_chips = list(map(lambda x: x["props"]["value"], children))
    filtered = list(filter(lambda d: d not in active_chips, current_chips))
    new_active_chips = list(filter(lambda x: x not in filtered, value))

    trigger_id = dash.ctx.triggered_id
    if trigger_id == "close-modal-btn" or trigger_id == "open-modal-btn":
        return not opened, new_children, new_active_chips
    return opened, children, active_chips

