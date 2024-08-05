import dash
import dash_mantine_components as dmc
from dash import Output, Input, State
from dash_iconify import DashIconify

from src.config.id_config import *
from src.main import app
from src.util.decorators import spaced_section


@spaced_section
def general_controls(args):
    return dmc.Stack([
        dmc.Group([
            dmc.Text("Theme (light / dark)", size="sm"),
            dmc.Switch(
                offLabel=DashIconify(icon="radix-icons:moon", width=16),
                onLabel=DashIconify(icon="radix-icons:sun", width=16),
                size="xs",
                id=ID_THEME_SWITCH
            )],
            justify="space-between",
        ),
    ],
        gap="xl",
        justify="space-between",
        style={"height": "100%"}
    )


@app.callback(
    Output(ID_APP_THEME, 'forceColorScheme'),
    Input(ID_THEME_SWITCH, "checked"),
    State(ID_APP_THEME, 'forceColorScheme'),
    prevent_intial_call=True
)
def switch_theme(checked, theme):
    return "dark" if theme == "light" else "light"
