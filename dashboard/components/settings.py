from datetime import datetime, date, timedelta

import dash_mantine_components as dmc
from dash import html, Output, Input
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from dashboard.config.settings_config import bricks, tags
from dashboard.maindash import app


def settings():
    return dmc.Container(
        children=[
            dmc.Center(dmc.Text("Mitwelten Discover", size="lg")),
            dmc.Space(h=30),
            dmc.Divider(label="Time Range Selection", labelPosition="center", size="md"),
            dmc.Space(h=10),
            dmc.Center(
                dmc.DateRangePicker(
                    id="date-range-picker",
                    label="Date Range",
                    description="",
                    minDate=date(2020, 8, 5),
                    value=[datetime.now().date(), datetime.now().date() + timedelta(days=5)],
                    style={"width": 250},
                ),
            ),
            dmc.Space(h=10),
            dmc.Center(dmc.Text(id="selected-date-date-range-picker", size="xs")),

            dmc.Space(h=30),
            dmc.Divider(label="Settings", labelPosition="center", size="md"),

            dmc.Space(h=10),
            dmc.CheckboxGroup(
                id="checkbox-group",
                label="Bricks",
                description="Select the displayed Bricks",
                orientation="vertical",
                withAsterisk=False,
                offset="xs",
                children=list(map(lambda x: dmc.Checkbox(label=x, value=x.lower()), bricks)),
                value=[],
            ),
            dmc.Text(id="checkbox-group-output"),
            dmc.Space(h=30),

            dmc.Text("Select the displayed TAG's", size="xs", color="gray"),
            dmc.Space(h=10),
            dmc.Center([
                dmc.ChipGroup(
                    [dmc.Chip(x, value=x) for x in tags],
                    multiple=True,
                    value=[],
                ),
            ]),
            html.Div(
                dmc.Switch(
                    offLabel=DashIconify(icon="radix-icons:moon", width=16),
                    onLabel=DashIconify(icon="radix-icons:sun", width=16),
                    size="xs",
                    id="theme-switch"
                ),
                id="theme-switch-container"
            )
        ],
        fluid=True,
        style={"height": "100vh"}
    )


@app.callback(
    Output("selected-date-date-range-picker", "children"),
    Input("date-range-picker", "value"),
)
def update_output(dates):
    prefix = "You have selected: "
    if dates:
        return prefix + "   -   ".join(dates)
    else:
        raise PreventUpdate


@app.callback(
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
