from datetime import datetime, timedelta

import dash
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Output, Input, dcc, State, html, callback, ALL
from dashboard.config.id import *

from dashboard.api.api_client import get_pollinator_timeseries
from dashboard.components.data_drawer.charts import create_themed_figure
from dashboard.maindash import app


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


def create_pollinator_figure(pollinator_class, trigger_id, bucket_width, light_mode):
    resp = get_pollinator_timeseries(
        pollinator_class=pollinator_class,
        deployment_id=trigger_id,
        confidence=0.9,
        bucket_width=bucket_width,
        time_from=(datetime.now() - timedelta(days=1000)).isoformat(),
        time_to=datetime.now().isoformat(),
    )
    figure = create_themed_figure(light_mode)
    figure.add_trace(go.Bar(
        x=resp["bucket"],
        y=resp["detections"],

    ))
    return figure


def create_graph(pollinator_class, trigger_id, light_mode):
    bucket_width = "1h"
    return dcc.Graph(
        figure=create_pollinator_figure(pollinator_class, trigger_id, bucket_width, light_mode),
        responsive=True,
        className="chart-graph",
    )


def create_pollinator_chart(_1, _2):
    enumerated_tabs = list(enumerate(tabs, 0))

    tab_list = [dmc.Tab(f"{tab['title']}", value=f"{idx}") for (idx, tab) in enumerated_tabs]

    return dmc.Tabs(
        [
            dmc.TabsList(tab_list, position="center"),
            html.Div(id="tabs-content")
        ],
        id="tabs-example",
        value="0",
        persistence=True,
        variant="outline",
    )


@callback(
    Output("tabs-content", "children"),
    Input("tabs-example", "value"),
    Input({"role": "Pollinator Cam", "label": "Store"}, "data"),
    State(ID_APP_THEME, "theme"),
)
def render_content(active, data, theme):
    return create_graph(tabs[int(active)]["pollinator_class"], data["deployment_id"], theme)


@app.callback(
    Output({"role": "Pollinator Cam", "label": "Store"}, "data"),
    Output(ID_FOCUS_ON_MAP_LOCATION, "data", allow_duplicate=True),
    Input({"role": "Pollinator Cam", "id": ALL, "label": "Node"}, "n_clicks"),
    State(ID_DEPLOYMENT_DATA_STORE, "data"),
    prevent_initial_call=True
)
def handle_pollinator_cam_click(_, data):
    data = data["Pollinator Cam"]
    if dash.ctx.triggered_id is not None:
        for note in data:
            if note["deployment_id"] == dash.ctx.triggered_id["id"]:
                return note, note["location"]

    return dash.no_update, dash.no_update


@app.callback(
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Input({"role": "Pollinator Cam", "label": "Store"}, "data"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def create_figure_from_store(data, light_mode):
    return create_pollinator_chart(data["deployment_id"], light_mode)
