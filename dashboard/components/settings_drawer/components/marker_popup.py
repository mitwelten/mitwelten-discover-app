
from datetime import datetime

import dash_mantine_components as dmc
from dash import html


def marker_popup(deployment, color):
    start = datetime.strftime(datetime.fromisoformat(deployment.period_start), '%d %b %Y - %H:%M')
    end = datetime.strftime(datetime.fromisoformat(deployment.period_start), '%d %b %Y - %H:%M') if deployment.period_end else "-"
    return dmc.Container([
        dmc.Group([
            dmc.Group([
                html.Div(
                    className="color-point",
                    style={"background": f"{color}"}
                ),
                dmc.Text(deployment.node_type, weight=700, size="sm"),
            ],
                position="left",
                spacing="sm"
            ),
            dmc.Text(deployment.node_label, size="sm"),
        ],
            position="apart"
        ),
        dmc.Space(h=10),
        dmc.Divider(),
        dmc.Space(h=10),
        dmc.Group([
            dmc.Text("Deployment ID", size="xs"),
            dmc.Text(
                deployment.deployment_id,
                size="xs",
                color="dimmed",
            ),
        ],
            position="apart"
        ),
        dmc.Group([
            dmc.Text("Start", size="xs"),
            dmc.Text(start, size="xs", color="dimmed"),
        ],
            position="apart"
        ),
        dmc.Group([
            dmc.Text("End", size="xs"),
            dmc.Text(end, size="xs", color="dimmed"),
        ],
            position="apart"
        ),
        dmc.Space(h=10),
        dmc.Group(
            children=[dmc.Badge(t, size="sm", variant="outline") for t in deployment.tags],
            spacing="xs"
        ),
    ],
        fluid=True,
        style={"width": "240px"}
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
            dmc.Text("Environment Data Point", weight=700, size="sm"),
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
