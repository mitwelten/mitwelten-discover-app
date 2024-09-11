import dash_mantine_components as dmc
from dash_mantine_components import DEFAULT_THEME
from dash import Output, Input


from src.model.url_parameter import UrlParameter
from src.components.settings_drawer.drawer_content import drawer_content
from src.config.app_config import BACKGROUND_COLOR, SETTINGS_DRAWER_WIDTH
from src.config.id_config import *
from src.main import app

light = {
        "content": {"background": BACKGROUND_COLOR},
        "header": {"background":  BACKGROUND_COLOR},
        }


def settings_drawer(params: UrlParameter, all_tags, active_device): 
    return dmc.Drawer(
            id=ID_SETTINGS_DRAWER,
            children=drawer_content(params, all_tags, active_device),
            opened=True,
            size=SETTINGS_DRAWER_WIDTH,
            padding="md",
            withOverlay=False,
            zIndex=200,
            lockScroll=False,
            bg=BACKGROUND_COLOR,
            styles={"body": {"height": "calc(100vh - 60px)"}, **light} # 60px of drawer header
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
        )
def update_drawer_bg(current):
    styles={"body": {"height": "calc(100vh - 60px)"}} # 60px of drawer header


    dark = {
        "content": {"background": DEFAULT_THEME["colors"]["dark"][7]},
        "header": {"background":  DEFAULT_THEME["colors"]["dark"][7]},
        }

    newStyles = {**styles, **dark} if current == "dark" else {**styles, **light}
    return newStyles
