from datetime import datetime, timedelta

from pprint import pprint
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb
from dash import Output, Input, State, html, callback, dcc
import dash_mantine_components as dmc
from plotly.graph_objs.layout import xaxis
from src.model.deployment import Deployment
from src.config.app_config import PAX_DESCRIPTION, SECONDARY_COLOR, app_theme
from src.components.data_drawer.header import bottom_drawer_content

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


def create_pollinator_chart2(marker_data, date_range, theme):
    d = Deployment(marker_data)
    resp = get_pollinator_heatmap(d.id, confidence=0.75, time_from=date_range["start"], time_to=date_range["end"])
    figure = create_themed_figure(theme)
    if resp is not None and len(resp["datapoints"]) != 0:
        figure.update_layout(
            xaxis_title="Month",
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
            [0, f"rgb{hex_to_rgb(app_theme['colors'][SECONDARY_COLOR][0])}"],
            [1, f"rgb{hex_to_rgb(app_theme['colors'][SECONDARY_COLOR][-1])}"]
        ]
        figure.add_trace(go.Heatmap(
            z=list(heat_data.values()),
            x=[str(value) for value in range(min(months), max(months) + 1)],
            y=types,
            colorscale=colorscale,
            opacity=0.8,
            text=list(heat_data.values()),
            texttemplate="%{text}",
        ))
        figure.update_xaxes(side="top")

    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        style={"height":"100%", "width": "100%"}
     )

    return [
        bottom_drawer_content("Pollinator", "tbd", d.tags, "pollinator.svg", theme, True), 
        dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        ),
    ]
