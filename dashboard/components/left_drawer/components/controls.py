import dash_mantine_components as dmc
from dash import html, callback, Output, Input
from dash_iconify import DashIconify

from dashboard.config.id_config import *
from dashboard.components.left_drawer.decorators import spaced_section


@spaced_section
def setting_controls():
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


@callback(
    Output(ID_APP_THEME, 'theme'),
    Input(ID_APP_THEME, 'theme'),
    Input(ID_THEME_SWITCH, "checked"),
    prevent_intial_call=True)
def switch_theme(theme, checked):
    if not checked:
        theme.update({'colorScheme': 'light'})
    else:
        theme.update({'colorScheme': 'dark'})
    return theme
