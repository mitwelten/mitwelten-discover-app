from datetime import date
from datetime import datetime, timedelta

import dash
import dash_mantine_components as dmc
from dash import html, Output, Input, dcc, State, ctx
from dash.exceptions import PreventUpdate

from src.model.url_parameter import UrlParameter
from src.config.app_config import PRIMARY_COLOR
from src.config.id_config import *
from src.config.settings_config import DEFAULT_DATE_RANGES
from src.main import app
from src.util.util import local_formatted_date
from src.url.parse import update_query_data

visible = {"display": "block"}
not_visible = {"display": "none"}


def date_time_section(params: UrlParameter):
    timerange = params.timerange
    start = params.start
    end = params.end

    if timerange == "custom":
        label_start = ""
        label_end   = ""
    else:
        label_start = local_formatted_date(datetime.isoformat(datetime.now() - timedelta(weeks=int(timerange))), date_format="%d %b %Y")
        label_end   = local_formatted_date(datetime.isoformat(datetime.now()), date_format="%d %b %Y")

    return html.Div([
        dcc.Store(
            id=ID_DATE_RANGE_STORE,
            data=dict(start=start, end=end)
        ),
        dmc.SegmentedControl(
            id=ID_DATE_RANGE_SEGMENT,
            color=PRIMARY_COLOR,
            value=timerange,
            fullWidth=True,
            data=DEFAULT_DATE_RANGES,
            size="xs"
        ),
        dmc.Space(h=20),
        dmc.Center([
            dmc.DatePicker(
                id=ID_DATE_RANGE_PICKER,
                description="",
                minDate=date(2020, 1, 1),
                value=[start, end],
                valueFormat="DD MMM, YY",
                type="range",
                styles={"root": {"width": 220}, "dropdown": {"left": -5, "zIndex": 999999}},
                style={"display": "block"} if timerange == "custom" else {"display": "none"},
            ),
            dmc.Text(
                f"{label_start} - {label_end}",
                id=ID_DATE_RANGE_LABEL,
                c="dimmed",
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
    if None in value:
        raise PreventUpdate
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
def update_picker_from_segment(weeks, picker_value):
    if ctx.triggered_id == ID_DATE_RANGE_PICKER and None in picker_value:
        raise PreventUpdate

    if weeks == "":
        raise PreventUpdate

    if weeks == "custom":
        start = datetime.fromisoformat(picker_value[0]).isoformat(timespec="seconds")
        end   = datetime.fromisoformat(picker_value[1]).isoformat(timespec="seconds")
        store_data=dict(start=start, end=end)
        return store_data, visible, not_visible, dash.no_update

    start = (datetime.now() - timedelta(weeks=int(weeks))).isoformat(timespec="seconds")
    end   = datetime.now().isoformat(timespec="seconds")
    store_data = dict(start=start, end=end)

    label_data_start = local_formatted_date(start, date_format="%d %b %Y")
    label_data_end   = local_formatted_date(end, date_format="%d %b %Y")
    return store_data, not_visible, visible, f"{label_data_start} - {label_data_end}"





@app.callback(
    Output(ID_QUERY_PARAM_STORE , "data", allow_duplicate=True),
    Input(ID_DATE_RANGE_STORE, "data"),
    Input(ID_DATE_RANGE_SEGMENT, "value"),
    State(ID_QUERY_PARAM_STORE , "data"),
    prevent_initial_call=True
)
def update_query_params(data, segment, params):
    if segment == "custom":
        return update_query_data(params, {"start": data["start"], "end": data["end"], "timerange": None})
    return update_query_data(params, {"start": None, "end": None, "timerange": segment})
    
