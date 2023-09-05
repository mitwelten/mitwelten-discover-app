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
