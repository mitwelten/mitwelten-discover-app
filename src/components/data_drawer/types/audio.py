from datetime import datetime, timedelta

from plotly.colors import hex_to_rgb
import plotly.graph_objects as go
import pandas as pd
from dash import dcc
import dash_mantine_components as dmc
from src.config.app_config import AUDIO_DESCRIPTION, SECONDARY_COLOR
from src.model.deployment import Deployment

from src.api.api_deployment import get_audio_timeseries, get_audio_top3, get_bird_stacked_bar
from src.components.data_drawer.header import bottom_drawer_content
from src.components.data_drawer.charts import create_themed_figure


def create_audio_chart(deployment_data, theme):

    d = Deployment(deployment_data)
    resp = get_audio_timeseries(
        taxon_id=212,
        deployment_id=d.id,
        bucket_width="1d",
        time_from=(datetime.now() - timedelta(days=1000)).isoformat(),
        time_to=datetime.now().isoformat(),
        confidence=0.9
    )

    figure = create_themed_figure(theme)

    if resp is not None and len(resp["bucket"]) != 0:
        figure.update_layout(
            annotations=[{"visible":False}],
            xaxis={"visible": True},
            yaxis={"visible": True},
        )
        figure.add_trace(go.Bar(
            x=resp["bucket"],
            y=resp["detections"],
        ))

    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",

    )
    return [
        bottom_drawer_content("Audio", "tbd", d.tags, "audio.svg", theme, test_icons=True), 
        dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        ),
    ]

def create_audio_chart2(deployment_data, theme):

    d = Deployment(deployment_data)
    resp = get_audio_top3(deployment_id=d.id)

    figure = create_themed_figure(theme)

    if resp is not None and len(resp) != 0:
        figure.update_layout(
            annotations=[{"visible":False}],
            xaxis={"visible": True},
            yaxis={"visible": True},
        )

        x=[value["count"] for value in resp]
        y=[value["species"] for value in resp]
        x.reverse()
        y.reverse()
        
                
        figure.add_trace(go.Bar(
            x=x,
            y=y,
            orientation="h",
            opacity=0.8,
            marker=dict(
                color=f"rgb{hex_to_rgb(theme['colors'][SECONDARY_COLOR][4])}",
                line=dict(color=f"rgb{hex_to_rgb(theme['colors'][SECONDARY_COLOR][-1])}", width=1)
            )
        ))

    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",

    )
    return [
        bottom_drawer_content("Audio", "tbd", d.tags, "audio.svg", theme, True), 
        dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        ),
    ]

def create_audio_chart3(deployment_data, date_range, theme):

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
        bottom_drawer_content("Audio", AUDIO_DESCRIPTION, d.tags, "test/audio.svg", theme, True), 
        dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        ),
    ]
