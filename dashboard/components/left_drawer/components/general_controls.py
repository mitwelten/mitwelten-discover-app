import dash
import dash_mantine_components as dmc
from dash import html, callback, Output, Input, State
from dash_iconify import DashIconify
from dashboard.maindash import app

from dashboard.config.id_config import *
from dashboard.util.decorators import spaced_section


@spaced_section
def general_controls():
    return html.Div([
        dmc.Group([
            dmc.Text("Theme (light / dark)", size="sm"),
            dmc.Switch(
                offLabel=DashIconify(icon="radix-icons:moon", width=16),
                onLabel=DashIconify(icon="radix-icons:sun", width=16),
                size="xs",
                id=ID_THEME_SWITCH
            )],
            position="apart",
        ),
    ])


@app.callback(
    Output(ID_APP_THEME, 'theme'),
    Input(ID_THEME_SWITCH, "checked"),
    State(ID_APP_THEME, 'theme'),
    prevent_intial_call=True
)
def switch_theme(checked, theme):
    if checked is None:
        return dash.no_update
    if not checked:
        theme.update({'colorScheme': 'light'})
    else:
        theme.update({'colorScheme': 'dark'})
    return theme
