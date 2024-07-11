import dash_mantine_components as dmc
from dash import Output, Input

from src.components.settings_drawer.drawer_content import drawer_content
from src.config.app_config import SETTINGS_DRAWER_WIDTH
from src.config.id_config import *
from src.main import app


def settings_drawer(args): 
    return dmc.Drawer(
            id=ID_SETTINGS_DRAWER,
            children=drawer_content(args),
            opened=True,
            size=SETTINGS_DRAWER_WIDTH,
            padding="md",
            withOverlay=False,
            zIndex=1000,
)


@app.callback(
    Output(ID_SETTINGS_DRAWER, "opened"),
    Input(ID_OPEN_SETTINGS_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_left_drawer(_):
    return True
