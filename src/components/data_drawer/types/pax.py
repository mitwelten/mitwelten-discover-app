import pandas as pd

import plotly.graph_objects as go
from dash import dcc
from src.model.deployment import Deployment
from datetime import datetime
import dash_mantine_components as dmc

from src.api.api_deployment import get_pax_timeseries
from src.components.data_drawer.charts import create_themed_figure


def create_pax_chart(marker_data, date_range, theme):
    print("date_range", date_range)
    start = datetime.fromisoformat(date_range["start"])
    end = datetime.fromisoformat(date_range["end"])
    delta_time = (end - start).days

    bucket_width = "1d"
    if delta_time <= 7:
        bucket_width = "15min"
    elif delta_time <= 30:
        bucket_width = "1h"


    d = Deployment(marker_data)
    resp = get_pax_timeseries(
        deployment_id=d.id,
        bucket_width=bucket_width,
        time_from=date_range["start"],
        time_to=date_range["end"]
    )

    figure = create_themed_figure(theme)

    if resp is not None and len(resp["buckets"]) != 0:

        figure.update_layout(
            yaxis_title="Number of People Detected",
            annotations=[{"visible":False}],
            xaxis={"visible": True},
            yaxis={"visible": True},
        )
        timeseries = pd.bdate_range(date_range["start"], date_range["end"], tz="UTC", freq=bucket_width)
        daten_df = pd.DataFrame(resp)
        daten_df['buckets'] = pd.to_datetime(daten_df['buckets'])
        full_df = pd.DataFrame(timeseries, columns=['buckets'])
        full_df = full_df.set_index('buckets').join(daten_df.set_index('buckets')).reset_index()

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
