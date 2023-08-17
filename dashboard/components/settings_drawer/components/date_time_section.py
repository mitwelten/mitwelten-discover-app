from datetime import date
from datetime import datetime, timedelta

import dash
import dash_mantine_components as dmc
from dash import html, Output, Input, dcc, State

from configuration import PRIMARY_COLOR
from dashboard.config.id import *
from dashboard.config.settings import DEFAULT_DATE_RANGES
from dashboard.config.settings import FIRST_DEPLOYMENT_WEEKS_AGO
from dashboard.maindash import app
from dashboard.util.decorators import spaced_section


@spaced_section
def date_time_section():
    return html.Div([
        dcc.Store(
            id=ID_DATE_RANGE_STORE,
            data=dict(
                start=datetime.now().date() - timedelta(weeks=FIRST_DEPLOYMENT_WEEKS_AGO),
                end=datetime.now().date()
            )
        ),
        dmc.SegmentedControl(
            id=ID_DATE_RANGE_SEGMENT,
            color=PRIMARY_COLOR,
            value="custom",
            fullWidth=True,
            data=DEFAULT_DATE_RANGES,
            mt=10,
            persistence=True
        ),
        dmc.Space(h=20),
        dmc.Center(
            dmc.DateRangePicker(
                id=ID_DATE_RANGE_PICKER,
                inputFormat="DD MMMM, YY",
                description="",
                minDate=date(2020, 8, 5),
                value=[datetime.now().date() - timedelta(weeks=FIRST_DEPLOYMENT_WEEKS_AGO), datetime.now().date()],
                styles={"root": {"width": 280}},
            ),
        )


    ])


@app.callback(
    Output(ID_DATE_RANGE_STORE, "data", allow_duplicate=True),
    Input(ID_DATE_RANGE_PICKER, "value"),
    prevent_initial_call=True
)
def change_visibility_of_date_range_picker(value):
    return dict(start=value[0], end=value[1])


@app.callback(
    Output(ID_DATE_RANGE_STORE, "data", allow_duplicate=True),
    Output(ID_DATE_RANGE_PICKER, "style"),
    Input(ID_DATE_RANGE_SEGMENT, "value"),
    State(ID_DATE_RANGE_PICKER, "value"),
    prevent_initial_call=True
)
def update_picker_from_segment(segment_data, picker_value):
    if segment_data == "":
        return dash.no_update, dash.no_update
    if segment_data == "custom":
        return dict(start=picker_value[0], end=picker_value[1]), {"display": "block"}

    if not segment_data:
        seg_time_range = 7
    else:
        seg_time_range = int(segment_data)

    return dict(start=datetime.now().date() - timedelta(weeks=seg_time_range), end=datetime.now().date()), {"display": "none"}

