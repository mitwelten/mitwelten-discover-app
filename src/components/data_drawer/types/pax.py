from datetime import datetime, timedelta

import plotly.graph_objects as go
from dash import dcc

from src.api.api_deployment import get_pax_timeseries
from src.components.data_drawer.charts import create_themed_figure


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
