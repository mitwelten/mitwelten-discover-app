import time
from datetime import datetime, timedelta
import plotly.graph_objects as go

import dash
import dash_mantine_components as dmc
import plotly.express as px
from dash import html, Output, Input, callback, ALL, State, dcc

from util.validations import cleanup_timeseries
from dashboard.api.api_client import get_env_timeseries, get_pax_timeseries
from dashboard.config.id_config import *
from dashboard.config.api_config import *
from dashboard.maindash import app
from util.functions import safe_reduce

fig = px.line()

modal_chart = html.Div([
    dcc.Store(id="figure-store", data=dict(fig=None)),
    dcc.Store(id=ID_MARKER_CLICK_STORE, data=dict(clicks=None)),
    dmc.Modal(
        title="Measurement Chart",
        id=ID_CHART_MODAL,
        centered=True,
        zIndex=10000,
        size="80%",
        closeOnClickOutside=True,
        closeOnEscape=True,
        children=[
            dmc.Container(
                dcc.Graph(
                    id=ID_MEASUREMENT_CHART,
                    figure=fig,
                    # config={"displayModeBar": False},
                    style={"height": "inherit", "width": "inherit"}
                ),
            )
        ],
    ),
    ])


def create_env_chart(trigger_id, light_mode = False):
    print("fetch env data - id: ", trigger_id)
    bucket_width = "1h"
    temp = get_env_timeseries(trigger_id, "temperature", "mean", bucket_width)
    hum = get_env_timeseries(trigger_id, "humidity", "mean", bucket_width)
    moi = get_env_timeseries(trigger_id, "moisture", "mean", bucket_width)
    temp = cleanup_timeseries(temp, TEMP_LOWER_BOUNDARY, TEMP_UPPER_BOUNDARY)
    hum = cleanup_timeseries(hum, HUM_LOWER_BOUNDARY, HUM_UPPER_BOUNDARY)
    moi = cleanup_timeseries(moi, MOI_LOWER_BOUNDARY, MOI_UPPER_BOUNDARY)

    new_figure = go.Figure()
    new_figure.add_trace(go.Scatter(
        x=temp['time'],
        y=temp['value'],
        name="Temperature"
    ))
    new_figure.add_trace(go.Scatter(
        x=hum['time'],
        y=hum['value'],
        yaxis='y2',
        name="Humidity"
    ))
    new_figure.add_trace(go.Scatter(
        x=moi['time'],
        y=moi['value'],
        yaxis='y3',
        name="Moisture"
    ))
    offset = 80
    new_figure.update_layout(
        xaxis=dict(domain=[0, 1]),
        yaxis=dict(
            title="Temperature",
        ),
        yaxis2=dict(
            title="Humidity",
            anchor="free",
            overlaying="y",
            shift=-offset,
        ),
        yaxis3=dict(
            title="Moisture",
            anchor="free",
            overlaying="y",
            shift=-2 * offset,
        ),
        template="plotly_white" if light_mode else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    # new_figure = px.line(
    #     temp,
    #     x='time',
    #     y="value",
    #     title=f"{dash.ctx.triggered_id['role']} - {dash.ctx.triggered_id['label']}",
    # )
    return new_figure


def create_pax_chart(trigger_id, light_mode=False):
    print("fetch pax data - id: ", trigger_id)
    resp = get_pax_timeseries(trigger_id, "1h", (datetime.now() - timedelta(days=3)).isoformat(), datetime.now().isoformat())
    new_figure = px.line(
        resp,
        x='buckets',
        y="pax",
        title=f"{dash.ctx.triggered_id['role']} - {dash.ctx.triggered_id['label']}",
    )
    new_figure.update_layout(template="plotly_white" if light_mode else "plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return new_figure



@app.long_callback(
    Output(ID_MEASUREMENT_CHART, "figure"),
    Output(ID_CHART_MODAL, "opened"),
    Output(ID_MARKER_CLICK_STORE, "data"),
    Input({"role": ALL, "id": ALL, "label": ALL}, "n_clicks"),
    Input(ID_MARKER_CLICK_STORE, "data"),
    State(ID_DATE_RANGE_PICKER, "value"),
    State(ID_CHART_MODAL, "opened"),
    State(ID_APP_THEME, "theme"),
    running=[
        (
                Output(ID_LOADER, "style"),
                {"visibility": "visible"},
                {"visibility": "hidden"},
        ),

    ],
    prevent_initial_call=True,
)
def marker_click(n_clicks, data, date, opened, theme):
    click_sum = safe_reduce(lambda x, y: x + y, n_clicks)
    # print(n_clicks, date, data, opened, dash.ctx.triggered_id)

    has_click_triggered = click_sum != data["clicks"]

    if click_sum is not None:
        data["clicks"] = click_sum

    if has_click_triggered and dash.ctx.triggered_id is not None:
        trigger_id = dash.ctx.triggered_id["id"]
        match dash.ctx.triggered_id["role"]:
            case "Env. Sensor": new_figure = create_env_chart(trigger_id,theme.get("colorScheme")=="light")
            case "Pax Counter": new_figure = create_pax_chart(trigger_id, theme.get("colorScheme")=="light")
            # case "Wild Cam": new_figure = create_wild_cam_chart(trigger_id)
            case _: return dash.no_update

        return new_figure, True, data
    return None, False, data

