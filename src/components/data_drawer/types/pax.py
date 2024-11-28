import pandas as pd

import plotly.graph_objects as go
from dash import dcc
from src.model.deployment import Deployment
from datetime import datetime, timezone
import dash_mantine_components as dmc

from src.api.api_deployment import get_pax_timeseries
from src.components.data_drawer.charts import create_themed_figure


def create_pax_chart(deployment_data, date_range, theme):

    date_str = date_range['start']
    try:
        start_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        start_time = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    end_time = datetime.strptime(date_range['end'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)

    deployment_start = datetime.fromisoformat(deployment_data['period']['start'])
    deployment_end = deployment_data['period'].get('end')
    deployment_end = datetime.fromisoformat(deployment_end) if deployment_end else None
    
    start = max(start_time, deployment_start)
    end = min(end_time, deployment_end) if deployment_end else end_time

    delta_time = (end - start).days

    bucket_width = "1d"
    if delta_time <= 7:
        bucket_width = "15min"
    elif delta_time <= 30:
        bucket_width = "1h"

    d = Deployment(deployment_data)
    resp = get_pax_timeseries(
        deployment_id=d.id,
        bucket_width=bucket_width,
        time_from=start,
        time_to=end
    )

    figure = create_themed_figure(theme)

    if resp is not None and len(resp["buckets"]) != 0:

        figure.update_layout(
            yaxis_title="Average of People Detected",
            annotations=[{"visible":False}],
            xaxis={"visible": True},
            yaxis={"visible": True},
        )
        timeseries = pd.bdate_range(start, end, tz="UTC", freq=bucket_width)
        data_df = pd.DataFrame(resp)
        data_df['buckets'] = pd.to_datetime(data_df['buckets'])
        full_df = pd.DataFrame(timeseries, columns=['buckets'])
        full_df = full_df.set_index('buckets').join(data_df.set_index('buckets')).reset_index()

        figure.add_trace(go.Bar(
            x=full_df["buckets"],
            y=full_df["pax"],
        ))
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        style={"width":"100%", "height":"100%"}
    )

    return dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        )
