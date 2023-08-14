import dash_mantine_components as dmc
from dash import Output, Input, State

from dashboard.components.settings_drawer.drawer_content import drawer_content
from dashboard.config.app import SETTINGS_DRAWER_WIDTH
from dashboard.config.id import *
from dashboard.maindash import app
from util.functions import ensure_marker_visibility


def settings_drawer(deployments, tags, deployment_markers):
    return dmc.Drawer(
        id=ID_SETTINGS_DRAWER,
        title=dmc.Title("Mitwelten Discover", align="center", order=1, style={"marginLeft":"20px"}),
        children=drawer_content(deployments, tags, deployment_markers),
        opened=True,
        size=SETTINGS_DRAWER_WIDTH,
        padding="md",
        closeOnClickOutside=False,
        closeOnEscape=False,
        withOverlay=False,
        zIndex=90000,
    )


@app.callback(
    Output(ID_SETTINGS_DRAWER, "opened"),
    Output(ID_SETTINGS_DRAWER, "position"),
    Output(ID_MAP, "center", allow_duplicate=True),
    Input(ID_OPEN_LEFT_DRAWER_BUTTON, "n_clicks"),
    State(ID_CURRENT_CHART_DATA_STORE, "data"),
    State(ID_MAP, "bounds"),
    State(ID_MAP, "center"),
    prevent_initial_call=True,
)
def open_left_drawer(_, chart_data, bounds, map_center):
    map_center = ensure_marker_visibility(map_center, bounds, chart_data)
    return True, "left", map_center
