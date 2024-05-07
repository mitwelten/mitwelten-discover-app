import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc

from src.model.deployment import Deployment
from src.components.data_drawer.header import bottom_drawer_content
from src.api.api_deployment import get_env_timeseries
from src.components.data_drawer.charts import create_themed_figure
from src.config.api_config import *
from src.util.validations import cleanup_timeseries


def create_env_temp_chart(trigger_id, bucket_width, light_mode):
    temp = get_env_timeseries(trigger_id, "temperature", "mean", bucket_width)
    temp = cleanup_timeseries(temp, TEMP_LOWER_BOUNDARY, TEMP_UPPER_BOUNDARY)
    figure = create_themed_figure(light_mode)

    if len(temp["value"]) == 0:
        return figure

    figure.update_layout(
        annotations=[{"visible":False}],
        xaxis={"visible": True},
        yaxis={"visible": True},
    )
    figure.add_trace(go.Scatter(
        x=temp["time"],
        y=temp["value"],
    ))
    return figure


def create_env_hum_chart(trigger_id, bucket_width, light_mode):
    hum = get_env_timeseries(trigger_id, "humidity", "mean", bucket_width)
    hum = cleanup_timeseries(hum, HUM_LOWER_BOUNDARY, HUM_UPPER_BOUNDARY)
    figure = create_themed_figure(light_mode)

    if len(hum["value"]) == 0:
        return figure

    figure.update_layout(
        annotations=[{"visible":False}],
        xaxis={"visible": True},
        yaxis={"visible": True},
    )
    figure.add_trace(go.Scatter(
        x=hum["time"],
        y=hum["value"],
    ))

    return figure


def create_env_moi_chart(trigger_id, bucket_width, light_mode):
    moi = get_env_timeseries(trigger_id, "moisture", "mean", bucket_width)
    moi = cleanup_timeseries(moi, MOI_LOWER_BOUNDARY, MOI_UPPER_BOUNDARY)
    figure = create_themed_figure(light_mode)

    if len(moi["value"]) == 0:
        return figure


    figure.update_layout(
        annotations=[{"visible":False}],
        xaxis={"visible": True},
        yaxis={"visible": True},
    )
    figure.add_trace(go.Scatter(
        x=moi["time"],
        y=moi["value"],
    ))
    return figure


def create_env_chart(deployment_data, theme):
    d = Deployment(deployment_data)
    bucket_width = "1h"
    tabs = [
        dict(
            title="Temperatur",
            fn=create_env_temp_chart
        ),
        dict(
            title="Humidity",
            fn=create_env_hum_chart
        ),
        dict(
            title="Moisture",
            fn=create_env_moi_chart
        ),
    ]

    enumerated_tabs = list(enumerate(tabs, 0))

    def create_graph(fn):
        return dcc.Graph(
            figure=fn(d.id, bucket_width, theme),
            responsive=True,
            className="chart-graph",
        )

    panel_list = [dmc.TabsPanel(
            create_graph(tab["fn"]),
            value=f"{idx}",
            className="chart-container"
    )
        for (idx, tab) in enumerated_tabs]

    tab_list = [dmc.Tab(f"{tab['title']}", value=f"{idx}") for (idx, tab) in enumerated_tabs]

    tabs = dmc.Tabs([dmc.TabsList(tab_list, position="center"), *panel_list],
                    value="0",
                    persistence=True,
                    variant="outline",
                    style={"height": "90%"})


    return [
        bottom_drawer_content("Environment Sensor", "tbd", d.tags, "environSensor.svg", theme), 
        dmc.Paper(
            children=tabs,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        ),
    ]
