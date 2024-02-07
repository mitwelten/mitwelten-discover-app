from datetime import datetime, timedelta

import plotly.graph_objects as go
from dash import dcc

from src.api.api_deployment import get_audio_timeseries
from src.components.data_drawer.charts import create_themed_figure


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
