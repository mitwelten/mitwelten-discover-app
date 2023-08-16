import dash
import dash_mantine_components as dmc
from dash import Output, Input, ALL, State
from dash import dcc

from dashboard.api.api_client import get_environment_data_by_id
from dashboard.components.data_drawer.charts import spider_chart
from dashboard.config.id import *
from dashboard.maindash import app


def create_environment_point_chart(legend, trigger_id, light_mode=True):
    resp = get_environment_data_by_id(trigger_id)
    values = [resp[key] for key in legend.keys()]
    labels = [legend[key]["label"] for key in legend.keys()]

    figure = spider_chart(labels, values, light_mode)
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",
    )
    return graph


def create_figure(env_point):
    return dmc.Text(f"Env Point {env_point}")
