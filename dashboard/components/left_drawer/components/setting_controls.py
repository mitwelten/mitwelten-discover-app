import dash_mantine_components as dmc
from dash import html, callback, Output, Input
from dash_iconify import DashIconify

from dashboard.components.left_drawer.components.decorators import spaced_section


@spaced_section
def setting_controls():
    return html.Div([
        dmc.Group([
            dmc.Text("Theme (light / dark)", size="sm"),
            dmc.Switch(
                offLabel=DashIconify(icon="radix-icons:moon", width=16),
                onLabel=DashIconify(icon="radix-icons:sun", width=16),
                size="xs",
                id="theme-switch"
            )],
            position="apart",
        ),
    ])


@callback(
    Output('app-theme', 'theme'),
    Input('app-theme', 'theme'),
    Input("theme-switch", "checked"),
    prevent_intial_call=True)
def switch_theme(theme, checked):
    if not checked:
        theme.update({'colorScheme': 'light'})
    else:
        theme.update({'colorScheme': 'dark'})
    return theme
