import json

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import html, Output, Input, callback, ALL, State, dcc
from dash_iconify import DashIconify

from dashboard.components.left_drawer.components.type_filter import brick_type_filter
from dashboard.components.left_drawer.components.date_time_section import date_time_section
from dashboard.components.left_drawer.components.controls import setting_controls
from dashboard.components.left_drawer.components.tag_filter import tag_filter
from dashboard.api.api_client import get_env_timeseries
from dashboard.config.id_config import *

from util.functions import safe_reduce

fig = px.line()

modal_chart = html.Div([
    dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(clicks=None)),
    dmc.Modal(
        title="Measurement Chart",
        id=ID_CHART_MODAL,
        centered=True,
        zIndex=10000,
        size="80%",
        closeOnClickOutside=True,
        closeOnEscape=False,
        children=[
            dmc.Container(
                dcc.Graph(
                    id=ID_MEASUREMENT_CHART,
                    figure=fig,
                    config={"displayModeBar": False},
                    style={"height": "inherit", "width": "inherit"}
                ),
            )
        ],
    ),
    ])


@callback(
    Output(ID_MEASUREMENT_CHART, "figure"),
    Output(ID_CHART_MODAL, "opened"),
    Output(ID_MARKER_CLICK_STORE, "data"),
    Input({"role": ALL, "id": ALL, "label": ALL}, "n_clicks"),
    Input(ID_DATE_RANGE_PICKER, "value"),
    Input(ID_MARKER_CLICK_STORE, "data"),
    State(ID_CHART_MODAL, "opened"),
    prevent_initial_call=True,
)
def marker_click(n_clicks, date, data, opened):
    click_sum = safe_reduce(lambda x, y: x + y, n_clicks)
    print(n_clicks, date, data, opened, dash.ctx.triggered_id)

    has_click_triggered = click_sum != data["clicks"]

    if click_sum is not None:
        data["clicks"] = click_sum

    if has_click_triggered and dash.ctx.triggered_id is not None:
        trigger_id = dash.ctx.triggered_id["id"]
        print(dash.ctx.triggered_id, opened)
        resp = get_env_timeseries(trigger_id, "temperature", "mean", "1h")
        resp["time"] = pd.to_datetime(resp["time"], format="%Y-%m-%d", exact=False)
        new_figure = px.line(
            resp,
            x='time',
            y="value",
            title=f"{dash.ctx.triggered_id['role']} - {dash.ctx.triggered_id['label']}",
        )
        return new_figure, True, data
    return dash.no_update
