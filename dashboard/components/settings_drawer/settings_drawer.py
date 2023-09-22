import dash_mantine_components as dmc
from dash import Output, Input

from dashboard.components.settings_drawer.drawer_content import drawer_content
from dashboard.config.app_config import SETTINGS_DRAWER_WIDTH
from dashboard.config.id_config import *
from dashboard.maindash import app


settings_drawer = dmc.Drawer(
    id=ID_SETTINGS_DRAWER,
    children=drawer_content,
    opened=True,
    size=SETTINGS_DRAWER_WIDTH,
    padding="md",
    withOverlay=False,
    zIndex=90000,
)


@app.callback(
    Output(ID_SETTINGS_DRAWER, "opened"),
    Input(ID_OPEN_LEFT_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_left_drawer(_):
    """
    Opens the settings drawer by click on the menu button.
    :return: The open state of the settings drawer.
    """
    return True
