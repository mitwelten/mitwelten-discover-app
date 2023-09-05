from datetime import datetime, timedelta

import dash
import plotly.graph_objects as go
from dash import Output, Input, ALL, State
from dash import dcc

from dashboard.api.api_client import get_audio_timeseries
from dashboard.components.data_drawer.charts import create_themed_figure
from dashboard.config.id import *
from dashboard.maindash import app


def create_audio_chart(trigger_id, light_mode=True):
    resp = get_audio_timeseries(
        taxon_id=212,
        deployment_id=trigger_id,
        bucket_width="1d",
        time_from=(datetime.now() - timedelta(days=1000)).isoformat(),
        time_to=datetime.now().isoformat(),
        confidence=0.9
    )
    figure = create_themed_figure(light_mode)
    figure.add_trace(go.Bar(
        x=resp["bucket"],
        y=resp["detections"],
    ))
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",
    )
    return graph



