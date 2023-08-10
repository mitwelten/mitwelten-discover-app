import dash_mantine_components as dmc
from dash import html

from dashboard.config.id import *


def chart_drawer():
    return dmc.Drawer(
        opened=False,
        id=ID_CHART_DRAWER,
        zIndex=20000,
        size="50%",
        closeOnClickOutside=False,
        closeOnEscape=False,
        withOverlay=False,
        className="chart-drawer",
        children=[
            dmc.LoadingOverlay(
                html.Div(id=ID_CHART_CONTAINER, className="measurement-chart", style={"margin": "20px"}),
                loaderProps={"variant": "dots", "color": "mitwelten_pink", "size": "xl"},
            )
        ],
    )
