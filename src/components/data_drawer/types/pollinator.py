from datetime import datetime, timedelta

import plotly.graph_objects as go
from dash import Output, Input, State, html, callback, dcc
import dash_mantine_components as dmc

from src.api.api_deployment import get_pollinator_timeseries
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


def create_pollinator_chart(_1, _2):
    enumerated_tabs = list(enumerate(tabs, 0))

    tab_list = [
        dmc.Tab(f"{tab['title']}", value=f"{idx}") for (idx, tab) in enumerated_tabs
    ]

    return dmc.Tabs(
        [
            dmc.TabsList(tab_list, position="center"),
            html.Div(id="tabs-content", className="chart-container"),
        ],
        id="tabs-example",
        value="0",
        persistence=True,
        variant="outline",
        style={"height": "90%"},
    )


@callback(
    Output("tabs-content", "children"),
    Input("tabs-example", "value"),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    State(ID_APP_THEME, "theme"),
)
def render_content(active, data, theme):
    return create_graph(
        tabs[int(active)]["pollinator_class"], data["data"]["id"], theme
    )
