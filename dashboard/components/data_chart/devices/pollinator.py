from datetime import datetime, timedelta

import dash_mantine_components as dmc
from dash import dcc

from dashboard.api.api_client import get_pollinator_timeseries
from dashboard.components.data_chart.chart import create_figure_from_timeseries


def create_pollinator_request(pollinator_class, trigger_id, bucket_width, light_mode):
    timeseries = get_pollinator_timeseries(
        pollinator_class=pollinator_class,
        deployment_id=trigger_id,
        confidence=0.9,
        bucket_width=bucket_width,
        time_from=(datetime.now() - timedelta(days=1000)).isoformat(),
        time_to=datetime.now().isoformat(),
    )
    return create_figure_from_timeseries(timeseries, light_mode, x_label="bucket", y_label="detections")


def create_pollinator_chart(trigger_id, light_mode=True):
    bucket_width = "1h"
    tabs = [
        dict(
            title="Fliege",
            pollinator_class="fliege"
        ),
        dict(
            title="Honigbiene",
            pollinator_class="honigbiene"
        ),
        dict(
            title="Hummel",
            pollinator_class="hummel"
        ),
        dict(
            title="Schwebfliege",
            pollinator_class="schwebfliege"
        ),
        dict(
            title="Wildbiene",
            pollinator_class="wildbiene"
        )
    ]
    enumerated_tabs = list(enumerate(tabs, 0))

    def create_graph(pollinator_class):
        return dcc.Graph(
            figure=create_pollinator_request(pollinator_class, trigger_id, bucket_width, light_mode),
            responsive=True,
            className="chart-graph",
        )
    panel_list = [dmc.TabsPanel(create_graph(tab["pollinator_class"]), value=f"{idx}") for (idx, tab) in enumerated_tabs]
    tab_list = [dmc.Tab(f"{tab['title']}", value=f"{idx}") for (idx, tab) in enumerated_tabs]

    return dmc.Tabs(
        [
            dmc.TabsList(tab_list, position="center"),
            *panel_list
        ],
        value="0",
        persistence=True,
        variant="outline",
    )
