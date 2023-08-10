from datetime import date
from datetime import datetime, timedelta

import dash
import dash_mantine_components as dmc
from dash import html, Output, Input, dcc, State

from dashboard.config.id import *
from dashboard.config.settings import DEFAULT_DATE_RANGES
from dashboard.config.settings import FIRST_DEPLOYMENT_WEEKS_AGO
from dashboard.maindash import app
from dashboard.util.decorators import spaced_section


@spaced_section
def date_time_section():
    return html.Div([
        dmc.SegmentedControl(
            id=ID_DATE_RANGE_SEGMENT,
            color="mitwelten_green",
            # value=f"{FIRST_DEPLOYMENT_WEEKS_AGO}",
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
                style={"width": 250},
                persistence=True
            ),
        ),
    ])


@app.callback(
    Output(ID_DATE_RANGE_STORE, "data"),
    Output(ID_DATE_RANGE_SEGMENT, "styles", allow_duplicate=True),
    Input(ID_DATE_RANGE_SEGMENT, "value"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def update_picker_from_segment(segment_data, light_mode):
    if segment_data == "":
        return dash.no_update

    if not segment_data:
        seg_time_range = 7
    else:
        seg_time_range = int(segment_data)

    return [datetime.now().date() - timedelta(weeks=seg_time_range), datetime.now().date()], ""


@app.callback(
    Output(ID_DATE_RANGE_PICKER, "value"),
    Output(ID_DATE_RANGE_SEGMENT, "styles", allow_duplicate=True),
    Output(ID_DATE_RANGE_SEGMENT, "value"),
    Input(ID_DATE_RANGE_PICKER, "value"),
    Input(ID_DATE_RANGE_STORE, "data"),
    State(ID_APP_THEME, "theme"),
    State(ID_DATE_RANGE_SEGMENT, "value"),
    prevent_initial_call=True
)
def update_segment_style(date_range, date_range_store, light_mode, segment_value):
    label_color = dmc.theme.DEFAULT_COLORS['gray'][7] if light_mode else dmc.theme.DEFAULT_COLORS['gray'][1]
    segment_styles = {
        "active": {"visibility": "hidden", },
        "labelActive": {"color": f"{label_color}!important"},
    }

    new_date_range = date_range
    if dash.ctx.triggered_id == ID_DATE_RANGE_STORE:
        segment_styles = {}
        new_date_range = date_range_store
    else:
        segment_value = ""

    return new_date_range, segment_styles, segment_value
