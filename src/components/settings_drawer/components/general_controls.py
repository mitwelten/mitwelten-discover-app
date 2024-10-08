import dash_mantine_components as dmc
from dash import Output, Input, State, ctx
from dash_iconify import DashIconify
from dash.exceptions import PreventUpdate

from src.config.id_config import *
from src.main import app


def general_controls():
    return dmc.Group(
            justify="space-between",
            gap="xs",
            children=[ 
                      dmc.Text("Light / Dark Theme", size="sm"),
                      dmc.Switch(
                          offLabel=DashIconify(icon="radix-icons:moon", width=16),
                          onLabel=DashIconify(icon="radix-icons:sun", width=16),
                          size="xs",
                          id=ID_THEME_SWITCH
                          )
                      ],
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
