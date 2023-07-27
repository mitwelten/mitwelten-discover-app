from datetime import datetime, date, timedelta

import dash_mantine_components as dmc
from dash import html

from dashboard.config.id_config import *
from dashboard.config.settings_config import DEFAULT_DATE_RANGES
from dashboard.config.settings_config import FIRST_DEPLOYMENT_WEEKS_AGO
from dashboard.util.decorators import spaced_section


@spaced_section
def date_time_section():
    return html.Div([
        dmc.SegmentedControl(
            id=ID_DATE_RANGE_SEGMENT,
            color="green",
            value=f"{FIRST_DEPLOYMENT_WEEKS_AGO}",
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
                value=[datetime.now().date() - timedelta(weeks=FIRST_DEPLOYMENT_WEEKS_AGO), datetime.now().date()],
                style={"width": 250},
            ),
        ),
    ])
