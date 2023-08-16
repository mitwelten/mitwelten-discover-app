from datetime import datetime, timedelta

import dash
import plotly.graph_objects as go
from dash import Output, Input, ALL, State
from dash import dcc

from dashboard.api.api_client import get_pax_timeseries
from dashboard.components.data_drawer.charts import create_themed_figure
from dashboard.config.id import *
from dashboard.maindash import app


def create_pax_chart(trigger_id, light_mode=True):
    resp = get_pax_timeseries(
        deployment_id=trigger_id,
        bucket_width="1h",
        time_from=(datetime.now() - timedelta(days=1000)).isoformat(),
        time_to=datetime.now().isoformat()
    )
    figure = create_themed_figure(light_mode)
    figure.add_trace(go.Scatter(
        x=resp["buckets"],
        y=resp["pax"],
    ))
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",
    )
    return graph


@app.callback(
    Output({"role": "Pax Counter", "label": "Store"}, "data"),
    Output(ID_FOCUS_ON_MAP_LOCATION, "data", allow_duplicate=True),
    Input({"role": "Pax Counter", "id": ALL, "label": "Node"}, "n_clicks"),
    State(ID_DEPLOYMENT_DATA_STORE, "data"),
    prevent_initial_call=True
)
def handle_pax_click(_, data):
    data = data["Pax Counter"]
    if dash.ctx.triggered_id is not None:
        for note in data:
            if note["deployment_id"] == dash.ctx.triggered_id["id"]:
                return note, note["location"]

    return dash.no_update, dash.no_update


@app.callback(
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Input({"role": "Pax Counter", "label": "Store"}, "data"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def create_figure_from_store(data, light_mode):
    return create_pax_chart(data["deployment_id"], light_mode)
