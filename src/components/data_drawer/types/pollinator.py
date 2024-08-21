from datetime import datetime, timedelta

import calendar as cal
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb
from dash import dcc
import dash_mantine_components as dmc
from src.model.deployment import Deployment
from src.config.app_config import SECONDARY_COLOR
from src.components.data_drawer.header import data_drawer_header

from src.config.map_config import get_source_props
from src.api.api_deployment import get_pollinator_heatmap, get_pollinator_timeseries
from src.components.data_drawer.charts import create_themed_figure
from src.config.id_config import *

tabs = [
    dict(title="Fliege", pollinator_class="fliege"),
    dict(title="Honigbiene", pollinator_class="honigbiene"),
    dict(title="Hummel", pollinator_class="hummel"),
    dict(title="Schwebfliege", pollinator_class="schwebfliege"),
    dict(title="Wildbiene", pollinator_class="wildbiene"),
]


def create_pollinator_figure(pollinator_class, trigger_id, bucket_width, light_mode):
    resp = get_pollinator_timeseries(
        pollinator_class=pollinator_class,
        deployment_id=trigger_id,
        confidence=0.9,
        bucket_width=bucket_width,
        time_from=(datetime.now() - timedelta(days=1000)).isoformat(),
        time_to=datetime.now().isoformat(),
    )
    if resp is None:
        return
    figure = create_themed_figure(light_mode)
    figure.add_trace(
        go.Bar(
            x=resp["bucket"],
            y=resp["detections"],
        )
    )
    return figure


def create_graph(pollinator_class, trigger_id, light_mode):
    bucket_width = "1h"
    return dcc.Graph(
        figure=create_pollinator_figure(
            pollinator_class, trigger_id, bucket_width, light_mode
        ),
        responsive=True,
        className="chart-graph",
    )


def create_pollinator_chart(marker_data, date_range, theme):
    d = Deployment(marker_data)
    resp = get_pollinator_heatmap(d.id, confidence=0.75, time_from=date_range["start"], time_to=date_range["end"])
    figure = create_themed_figure(theme)
    if resp is not None and len(resp["datapoints"]) != 0:
        figure.update_layout(
            annotations=[{"visible":False}],
            xaxis={"visible": True},
            yaxis={"visible": True},
        )

        types = ["Fliege", "Honigbiene", "Hummel", "Schwebfliege", "Wildbiene"]
        months = [it["month"] for it in resp["datapoints"]]
        

        nof_month = max(months) - min(months) + 1
        heat_data = {t: [0] * nof_month for t in types}

        for t in types:
            for entry in resp["datapoints"]:
                if entry["class"] == t.lower():
                    heat_data[t][int(entry["month"]) - min(months)] = int(entry["count"])

        colorscale=[
            [0, f"rgb{hex_to_rgb('#FCE4EC')}"],
            [1, f"rgb{hex_to_rgb('#880E4F')}"]
        ]
        figure.add_trace(go.Heatmap(
            z=list(heat_data.values()),
            x=[cal.month_name[value] for value in range(min(months), max(months) + 1)],
            y=types,
            colorscale=colorscale,
            opacity=0.8,
            text=list(heat_data.values()),
            texttemplate="%{text}",
            
        ))
        figure.update_xaxes(side="top")
        figure.update_layout(margin_pad=20, font_size=12)

    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        style={"height":"100%", "width": "100%"}
     )

    return dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        )
