import dash
import dash_mantine_components as dmc
from dash import Output, Input, State, ctx
from dash_iconify import DashIconify
from dash.exceptions import PreventUpdate

from src.config.id_config import *
from src.main import app
from src.util.decorators import spaced_section


def general_controls(args):
    return dmc.Stack([
        dmc.Group([
            dmc.Text("Light / Dark Theme", size="sm"),
            dmc.Switch(
                offLabel=DashIconify(icon="radix-icons:moon", width=16),
                onLabel=DashIconify(icon="radix-icons:sun", width=16),
                size="xs",
                id=ID_THEME_SWITCH
            )],
                  justify="space-between",
        ),
        #dmc.Group([
        #    dmc.Text("Found a bug?", size="sm"),
        #    dmc.Anchor(
        #        "Submit an issue",
        #        href="https://github.com/mitwelten/mitwelten-discover-app/issues",
        #        target="_blank",
        #        size="sm"),
        #    ])
    ],
        gap="xs",
    )


@app.callback(
    Output(ID_APP_THEME, 'forceColorScheme'),
    Input(ID_THEME_SWITCH, "checked"),
    State(ID_APP_THEME, 'forceColorScheme'),
    prevent_intial_call=True
)
def switch_theme(checked, theme):
    if ctx.triggered_id == None:
        raise PreventUpdate
    return "dark" if theme == "light" else "light"
