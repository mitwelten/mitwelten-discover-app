from datetime import datetime, date, timedelta

import dash_mantine_components as dmc
from dash import html

from dashboard.components.left_drawer.components.decorators import spaced_section


@spaced_section
def date_time_section():
    return html.Div([
        dmc.SegmentedControl(
            id="segmented-time-range",
            color="green",
            value="1",
            fullWidth=True,
            data=[
                {"value": "100000", "label": "All"},
                {"value": "52", "label": "12 M"},
                {"value": "26", "label": "6 M"},
                {"value": "12", "label": "3 M"},
                {"value": "4", "label": "1 M"},
                {"value": "1", "label": "1 W"},
            ],
            mt=10,
        ),
        dmc.Space(h=20),
        dmc.Center(
            dmc.DateRangePicker(
                id="date-range-picker",
                label="Date Range",
                inputFormat="DD MMMM, YY",
                description="",
                minDate=date(2020, 8, 5),
                value=[datetime.now().date() - timedelta(days=7), datetime.now().date()],
                style={"width": 250},
            ),
        ),
    ],
    )
