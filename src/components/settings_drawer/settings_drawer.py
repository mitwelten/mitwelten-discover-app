import dash_mantine_components as dmc
from dash_mantine_components import DEFAULT_THEME
from dash import Output, Input, State
from dash.exceptions import PreventUpdate
from pprint import pprint


from src.components.settings_drawer.drawer_content import drawer_content
from src.config.app_config import BACKGROUND_COLOR, SETTINGS_DRAWER_WIDTH
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
            zIndex=200,
            lockScroll=False,
            bg=BACKGROUND_COLOR,
            styles={"body": {"height": "calc(100vh - 60px)"}} # 60px of drawer header
)


@app.callback(
    Output(ID_SETTINGS_DRAWER, "opened"),
    Input(ID_OPEN_SETTINGS_DRAWER_BUTTON, "n_clicks"),
    prevent_initial_call=True,
)
def open_left_drawer(_):
    return True


@app.callback(
        Output(ID_SETTINGS_DRAWER, "styles"),
        Input(ID_APP_THEME, "forceColorScheme"),
        prevent_initial_call=True,
        )
def update_drawer_bg(current):
    styles={"body": {"height": "calc(100vh - 60px)"}} # 60px of drawer header


    dark = {
        "content": {"background": DEFAULT_THEME["colors"]["dark"][7]},
        "header": {"background":  DEFAULT_THEME["colors"]["dark"][7]},
        }

    light = {
        "content": {"background": BACKGROUND_COLOR},
        "header": {"background":  BACKGROUND_COLOR},
        }

    newStyles = {**styles, **dark} if current == "dark" else {**styles, **light}
    return newStyles
