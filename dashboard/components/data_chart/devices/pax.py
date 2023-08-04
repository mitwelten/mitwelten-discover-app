from datetime import datetime, timedelta

import plotly.express as px
from dash import dcc

from dashboard.api.api_client import get_pax_timeseries
from dashboard.components.data_chart.chart import create_figure_from_timeseries


def create_pax_chart(trigger_id, light_mode=True):
    print("fetch pax data - id: ", trigger_id)
    resp = get_pax_timeseries(
        deployment_id=trigger_id,
        bucket_width="1h",
        time_from=(datetime.now() - timedelta(days=1000)).isoformat(),
        time_to=datetime.now().isoformat()
    )
    figure = create_figure_from_timeseries(resp, light_mode, x_label="buckets", y_label="pax")
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",
    )
    return graph
