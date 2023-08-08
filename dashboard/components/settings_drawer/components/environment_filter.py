from datetime import datetime

import dash_leaflet as dl
import dash_mantine_components as dmc
from dash import Output, Input, State, html

from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.environment import Environment
from dashboard.util.decorators import spaced_section


@spaced_section
def environment_filter():
    return dmc.Group([
        dmc.Group([
            html.Div(
                className="color-point",
                style={"background": "#946000"}
            ),
            dmc.Text("Environment Data Points", size="sm"),
        ]),
        dmc.Switch(
            size="xs",
            id=ID_ENVIRONMENT_SWITCH
        )],
        position="apart",
        )


def environment_popup(environment):
    created_at = datetime.strftime(datetime.fromisoformat(environment.created_at), '%d %b %Y - %H:%M')
    updated_at = datetime.strftime(datetime.fromisoformat(environment.updated_at), '%d %b %Y - %H:%M') if environment.updated_at else "-"
    return dmc.Container([
        dmc.Group([
            html.Div(
                className="color-point",
                style={"background": "#abde00"}
            ),
            dmc.Text("Environment Datapoint", weight=700, size="sm"),
        ],
            position="left",
            spacing="sm"
        ),
        dmc.Space(h=10),
        dmc.Divider(),
        dmc.Space(h=10),
        dmc.Group([
            dmc.Text("ID", size="xs"),
            dmc.Text(
                environment.environment_id,
                size="xs",
                color="dimmed",
            ),
        ],
            position="apart"
        ),
        dmc.Group([
            dmc.Text("Created", size="xs"),
            dmc.Text(created_at, size="xs", color="dimmed"),
        ],
            position="apart"
        ),
        dmc.Group([
            dmc.Text("Updated", size="xs"),
            dmc.Text(updated_at, size="xs", color="dimmed"),
        ],
            position="apart"
        ),
    ],
        fluid=True,
        style={"width": "220px"}
    )


@app.callback(
    Output(ID_ENV_LAYER_GROUP, "children"),
    Input(ID_ENVIRONMENT_SWITCH, "checked"),
    State(ID_ENV_DATA_STORE, "data"),
)
def add_environment_markers(checked, data):
    if not checked:
        return []
    markers = []

    for e in data:
        e = Environment(e)
        markers.append(
            dl.Marker(
                position=[e.lat, e.lon],
                children=[
                    dl.Popup(
                        children=[environment_popup(e)],
                        closeButton=False
                    ),
                    dl.Tooltip(
                        children=f"Environment Data: {e.environment_id}",
                        offset={"x": -10, "y": 2},
                        direction="left",
                    ),
                ],
                icon=dict(iconUrl=f"assets/markers/environment.svg", iconAnchor=[15, 6], iconSize=30),
                id={"role": "Environment", "id": e.environment_id, "label": ""},
            )
        )
    return markers
