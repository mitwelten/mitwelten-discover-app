import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State
from dash_iconify import DashIconify
import dash_core_components as dcc

from dashboard.config import api_config as api


def tag_filter(data):
    return html.Div([
        dcc.Store(id="current_tags_data", data=api.DEFAULT_TAGS),
        dmc.Group([
            dmc.Text("Select visible TAG's", size="xs", color="dimmed", style={"display": "inline-block"}),
            dmc.ActionIcon(
                DashIconify(
                    icon="material-symbols:add",
                    color=dmc.theme.DEFAULT_COLORS["green"][9],
                ),
                variant="outline",
                size="xs",
                id="open-modal-btn",
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
                value=api.DEFAULT_TAGS,
                id="chips-group",
            ),
            html.Div(
                dmc.Modal(
                    title="Select Tag's",
                    id="chip-modal",
                    zIndex=10000,
                    overflow="inside",
                    children=[
                        dmc.ChipGroup(
                            [dmc.Chip(x, value=x, size="xs") for x in sorted(data)],
                            multiple=True,
                            value=api.DEFAULT_TAGS,
                            id="modal-chips-group",
                        ),
                        dmc.Space(h=20),
                        dmc.Center(dmc.Button("Add", id="close-modal-btn")),
                    ],
                ),
            ),
        ]),
    ])


@callback(
    Output("chip-modal", "opened"),
    Output("chips-group", "children"),
    Output("chips-group", "value"),
    Input("open-modal-btn", "n_clicks"),
    Input("close-modal-btn", "n_clicks"),
    Input("modal-chips-group", "value"),
    Input("chips-group", "value"),
    Input("chips-group", "children"),
    State("chip-modal", "opened"),
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

