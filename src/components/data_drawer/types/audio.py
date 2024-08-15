from datetime import datetime, timedelta

from plotly.colors import hex_to_rgb
import plotly.graph_objects as go
import pandas as pd
from dash import dcc
import dash_mantine_components as dmc
from src.config.app_config import AUDIO_DESCRIPTION, SECONDARY_COLOR
from src.model.deployment import Deployment
from src.config.map_config import get_source_props

from src.api.api_deployment import get_audio_timeseries, get_audio_top3, get_bird_stacked_bar
from src.components.data_drawer.header import bottom_drawer_content
from src.components.data_drawer.charts import create_themed_figure

def create_audio_chart(deployment_data, date_range, theme):

    d = Deployment(deployment_data)
    resp = get_bird_stacked_bar(
        deployment_id=d.id,
        time_from=date_range["start"],
        time_to=date_range["end"],
        bucket_width="1d",
        confidence=0.9,
    )

    figure = create_themed_figure(theme)

    if resp is not None and len(resp) != 0:
        figure.update_layout(
            annotations=[{"visible":False}],
            xaxis={"visible": True},
            yaxis={"visible": True},
        )

        df = pd.DataFrame(resp)

        bars = []
        for group, dfg in df.groupby(by='species'):
            x=dfg['bucket']
            y=dfg['count']
            bars.append(go.Bar(name=group,x=x, y=y))

        timeseries = pd.bdate_range(date_range["start"], date_range["end"], tz="UTC", freq="D")

        figure.add_traces(bars)
        figure.add_traces(go.Bar(x=timeseries, y=[0] * len(timeseries)))
        figure.update_layout(barmode='stack', margin_pad=20, font_size=12)
                
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",

    )
    return [
        bottom_drawer_content(
            get_source_props("Audio Logger")["name"], 
            d.tags, 
            "audioLogger.svg", 
            theme), 
        dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        ),
    ]
