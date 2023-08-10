import dash_mantine_components as dmc
from dash import Output, Input, html, ALL

from dashboard.config.id import *
from dashboard.maindash import app


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


@app.callback(
    Output(ID_BOTTOM_DRAWER, "opened", allow_duplicate=True),
    Output(ID_BOTTOM_DRAWER, "position", allow_duplicate=True),
    Input(ID_BOTTOM_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_bottom_drawer(_):
    return True, "bottom"


@app.callback(
    Output(ID_BOTTOM_DRAWER, "opened", allow_duplicate=True),
    Output(ID_BOTTOM_DRAWER, "position", allow_duplicate=True),
    Input(ID_MAP, "click_lat_lng"),
    Input({'role': ALL, 'index': ALL, 'place': "drawer"}, 'n_clicks'),
    prevent_initial_call=True,
)
def open_bottom_drawer(_1, _2):
    return False, "bottom"
