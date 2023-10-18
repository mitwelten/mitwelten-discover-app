from dash import dcc

from dashboard.api.api_environment import get_environment_data_by_id
from dashboard.components.data_drawer.charts import spider_chart


def create_environment_point_chart(legend, trigger_id, light_mode=True):
    resp = get_environment_data_by_id(trigger_id)
    values = [resp[key] for key in legend.keys()]
    labels = [legend[key]["label"] for key in legend.keys()]

    figure = spider_chart(labels, values, light_mode)
    return dcc.Graph(
            figure=figure,
            responsive=True,
            className="chart-graph",
        )
