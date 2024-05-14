from datetime import date
from datetime import datetime, timedelta

import dash
import dash_mantine_components as dmc
from dash import html, Output, Input, dcc, State
from dash.exceptions import PreventUpdate

from src.config.app_config import PRIMARY_COLOR
from src.config.id_config import *
from src.config.settings_config import DEFAULT_DATE_RANGES
from src.config.settings_config import FIRST_DEPLOYMENT_WEEKS_AGO
from src.main import app
from src.util.decorators import spaced_section
from src.util.util import local_formatted_date, update_query_data


@spaced_section
def date_time_section(args):
    timerange = args.get("timerange", "custom")

    if args.get("start") is None or args.get("end") is None:
        start = datetime.now() - timedelta(weeks=FIRST_DEPLOYMENT_WEEKS_AGO)
        end = datetime.now()
    else:
        start = datetime.fromisoformat(args.get("start"))
        end   = datetime.fromisoformat(args.get("end"))

    if timerange == "custom":
        label_start = local_formatted_date(start.isoformat(), '%d %b %Y')
        label_end   = local_formatted_date(end.isoformat(), '%d %b %Y')
    else:
        label_start = local_formatted_date(datetime.isoformat(datetime.now() - timedelta(weeks=int(timerange))), "%d %b %Y")
        label_end   = local_formatted_date(datetime.isoformat(datetime.now()), "%d %b %Y")

    return html.Div([
        dcc.Store(
            id=ID_DATE_RANGE_STORE,
            data=dict(start=start.isoformat(timespec="seconds"), end=end.isoformat(timespec="seconds"))
        ),
        dmc.SegmentedControl(
            id=ID_DATE_RANGE_SEGMENT,
            color=PRIMARY_COLOR,
            value=timerange,
            fullWidth=True,
            data=DEFAULT_DATE_RANGES,
            mt=10,
            size="xs"
        ),
        dmc.Space(h=20),
        dmc.Center([
            dmc.DateRangePicker(
                id=ID_DATE_RANGE_PICKER,
                inputFormat="DD MMM, YY",
                description="",
                minDate=date(2020, 1, 1),
                value=[start, end],
                styles={"root": {"width": 220}},
                style={"display": "block"} if timerange == "custom" else {"display": "none"},
            ),
            dmc.Text(
                f"{label_start }- {label_end}",
                id=ID_DATE_RANGE_LABEL,
                color="dimmed",
                size="sm",
                style={"display": "none"} if timerange == "custom" else {"display": "block"},
            )
            ],
            style={"height": "40px"}
        ),

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
    Output(ID_DATE_RANGE_LABEL, "style"),
    Output(ID_DATE_RANGE_LABEL, "children"),
    Input(ID_DATE_RANGE_SEGMENT, "value"),
    Input(ID_DATE_RANGE_PICKER, "value"),
    prevent_initial_call=True
)
def update_picker_from_segment(segment_data, picker_value):
    if segment_data == "":
        raise PreventUpdate
    if segment_data == "custom":
        start = datetime.fromisoformat(picker_value[0]).isoformat(timespec="seconds")
        end   = datetime.fromisoformat(picker_value[1]).isoformat(timespec="seconds")
        store_data=dict(start=start, end=end)
        return store_data, {"display": "block"}, {"display": "none"}, dash.no_update

    if not segment_data:
        seg_time_range = 7
    else:
        seg_time_range = int(segment_data)

    start = (datetime.now() - timedelta(weeks=seg_time_range)).isoformat(timespec="seconds")
    end   = datetime.now().isoformat(timespec="seconds")
    store_data = dict(start=start, end=end)

    label_data_start = local_formatted_date(datetime.isoformat(datetime.now() - timedelta(weeks=seg_time_range)), "%d %b %Y")
    label_data_end   = local_formatted_date(datetime.isoformat(datetime.now()), "%d %b %Y")
    return store_data, {"display": "none"}, {"display": "block"}, f"{label_data_start} - {label_data_end}"

@app.callback(
    Output(ID_QUERY_PARAM_STORE , "data"),
    Input(ID_DATE_RANGE_STORE, "data"),
    Input(ID_DATE_RANGE_SEGMENT, "value"),
    State(ID_QUERY_PARAM_STORE , "data"),
)
def update_query_params(data, segment, params):
    if segment == "custom":
        print(data)
        return update_query_data(params, {"start": data["start"], "end": data["end"], "timerange": "custom"})
    return update_query_data(params, {"start": None, "end": None, "timerange": segment})
    
