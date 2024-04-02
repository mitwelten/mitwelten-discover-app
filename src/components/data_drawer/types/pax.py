from datetime import datetime, timedelta

import plotly.graph_objects as go
from dash import dcc
from src.config.app_config import PAX_DESCRIPTION
from src.model.deployment import Deployment
from src.components.data_drawer.header import bottom_drawer_content
import dash_mantine_components as dmc

from src.api.api_deployment import get_pax_timeseries
from src.components.data_drawer.charts import create_themed_figure


def create_pax_chart(marker_data, date_range, light_mode=True):
    d = Deployment(marker_data)
    resp = get_pax_timeseries(
        deployment_id=d.id,
        bucket_width="1h",
        time_from=date_range["start"],
        time_to=date_range["end"]
    )
    figure = create_themed_figure(light_mode)
    figure.update_layout(yaxis_title="Number of People Detected")
    figure.add_trace(go.Bar(
        x=resp["buckets"],
        y=resp["pax"],
    ))
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        style={"width":"100%", "height":"100%"}
    )
    return [
        bottom_drawer_content("PAX Counter", PAX_DESCRIPTION, d.tags, date_range["start"], date_range["end"], "PAX.svg", True), 
        dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        ),
    ]

