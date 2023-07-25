from datetime import datetime, date, timedelta

import dash_mantine_components as dmc
from dash import html

from dashboard.components.left_drawer.decorators import spaced_section
from dashboard.config.id_config import *
from dashboard.config.settings_config import DEFAULT_DATE_RANGES


@spaced_section
def date_time_section():
    return html.Div([
        dmc.SegmentedControl(
            id=ID_DATE_RANGE_SEGMENT,
            color="green",
            value="1",
            fullWidth=True,
            data=DEFAULT_DATE_RANGES,
            mt=10,
        ),
        dmc.Space(h=20),
        dmc.Center(
            dmc.DateRangePicker(
                id=ID_DATE_RANGE_PICKER,
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
