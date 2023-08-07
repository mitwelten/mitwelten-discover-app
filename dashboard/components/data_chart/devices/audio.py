from datetime import datetime, timedelta

from dash import dcc

from dashboard.api.api_client import get_audio_timeseries
from dashboard.components.data_chart.chart import create_figure_from_timeseries


def create_audio_chart(trigger_id, light_mode=True):
    resp = get_audio_timeseries(
        taxon_id=212,
        deployment_id=trigger_id,
        bucket_width="1d",
        time_from=(datetime.now() - timedelta(days=1000)).isoformat(),
        time_to=datetime.now().isoformat(),
        confidence=0.9
    )
    figure = create_figure_from_timeseries(resp, light_mode, x_label="bucket", y_label="detections")
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",
    )
    return graph
