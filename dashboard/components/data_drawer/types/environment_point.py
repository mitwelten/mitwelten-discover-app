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


@app.callback(
    Output({"role": "Environment", "label": "Store"}, "data"),
    Output(ID_FOCUS_ON_MAP_LOCATION, "data", allow_duplicate=True),
    Input({"role": "Environment", "id": ALL, "label": "Node"}, "n_clicks"),
    State(ID_ENV_DATA_STORE, "data"),
    State(ID_ENVIRONMENT_LEGEND_STORE, "data"),
    prevent_initial_call=True
)
def handle_environment_point_click(_, data, legend):
    if dash.ctx.triggered_id is not None:
        for env_point in data:
            if env_point["environment_id"] == dash.ctx.triggered_id["id"]:
                return env_point, env_point["location"]

    return dash.no_update, dash.no_update


@app.callback(
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Input({"role": "Environment", "label": "Store"}, "data"),
    State(ID_ENVIRONMENT_LEGEND_STORE, "data"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def create_figure_from_store(data, legend, light_mode):
    return create_environment_point_chart(legend, data["environment_id"], light_mode)
