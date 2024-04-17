from dash import dcc

from src.api.api_environment import get_environment_data_by_id
from src.components.data_drawer.charts import spider_chart
from src.components.data_drawer.header import bottom_drawer_content
import dash_mantine_components as dmc


def create_environment_point_chart(legend, id, theme):

    resp = get_environment_data_by_id(id)

    if resp is None:
        return

    values = [resp[key] for key in legend.keys()]
    labels = [legend[key]["label"] for key in legend.keys()]

    figure = spider_chart(labels, values, theme)
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",
    )

    return [
        bottom_drawer_content("Environment", "tbd", [], "habitat1.svg", theme, test_icons=True), 
        dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        ),
    ]
