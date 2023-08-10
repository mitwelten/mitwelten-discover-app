import dash_mantine_components as dmc
from dash import Output, Input

from dashboard.components.settings_drawer.drawer_content import drawer_content
from dashboard.config.app import SETTINGS_DRAWER_WIDTH
from dashboard.config.id import *
from dashboard.maindash import app


def settings_drawer(deployments, tags, deployment_markers):
    return dmc.Drawer(
        id=ID_SETTINGS_DRAWER,
        title=dmc.Title("Mitwelten Discover", align="center", order=1, style={"margin-left":"20px"}),
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
    Input(ID_OPEN_LEFT_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_left_drawer(_):
    return True, "left"
