import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, html

from dashboard.api.api_client import get_env_timeseries
from dashboard.components.data_drawer.charts import create_themed_figure
from dashboard.config.api import *
from util.validations import cleanup_timeseries


def create_env_temp_chart(trigger_id, bucket_width, light_mode):
    temp = get_env_timeseries(trigger_id, "temperature", "mean", bucket_width)
    temp = cleanup_timeseries(temp, TEMP_LOWER_BOUNDARY, TEMP_UPPER_BOUNDARY)
    figure = create_themed_figure(light_mode)
    figure.add_trace(go.Scatter(
        x=temp["time"],
        y=temp["value"],
    ))
    return figure


def create_env_hum_chart(trigger_id, bucket_width, light_mode):
    hum = get_env_timeseries(trigger_id, "humidity", "mean", bucket_width)
    hum = cleanup_timeseries(hum, HUM_LOWER_BOUNDARY, HUM_UPPER_BOUNDARY)
    figure = create_themed_figure(light_mode)
    figure.add_trace(go.Scatter(
        x=hum["time"],
        y=hum["value"],
    ))
    return figure


def create_env_moi_chart(trigger_id, bucket_width, light_mode):
    moi = get_env_timeseries(trigger_id, "moisture", "mean", bucket_width)
    moi = cleanup_timeseries(moi, MOI_LOWER_BOUNDARY, MOI_UPPER_BOUNDARY)
    figure = create_themed_figure(light_mode)
    figure.add_trace(go.Scatter(
        x=moi["time"],
        y=moi["value"],
    ))
    return figure


def create_env_chart(trigger_id, light_mode=True):
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
            figure=fn(trigger_id, bucket_width, light_mode),
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

    return dmc.Tabs([dmc.TabsList(tab_list, position="center"), *panel_list],
                    value="0",
                    persistence=True,
                    variant="outline",
                    style={"height": "100%"}
                    )
