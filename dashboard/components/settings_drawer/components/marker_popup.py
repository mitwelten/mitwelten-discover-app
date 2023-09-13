import dash_mantine_components as dmc
from dash import html

from dashboard.util.util import pretty_date


def header(source_id, source_type, label, color):
    return [dmc.Group([
        dmc.Group([
            html.Div(
                className="color-point",
                style={"background": f"{color}"}
            ),
            dmc.Text(source_type, weight=700, size="sm"),
        ],
            position="left",
            spacing="sm"
        ),
        dmc.Text(label, size="sm"),
    ],
        position="apart"
    ),
        dmc.Space(h=10),
        dmc.Divider(),
        dmc.Space(h=10),
        dmc.Group([
            dmc.Text("ID", size="xs"),
            dmc.Text(
                source_id,
                size="xs",
                color="dimmed",
            ),
        ],
            position="apart"
        )]


def time_section(fst_label, fst_time, snd_label, snd_time):
    return [
        dmc.Group([
            dmc.Text(fst_label, size="xs"),
            dmc.Text(fst_time, size="xs", color="dimmed"),
        ],
            position="apart"
        ),
        dmc.Group([
            dmc.Text(snd_label, size="xs"),
            dmc.Text(snd_time, size="xs", color="dimmed"),
        ],
            position="apart"
        ),
        dmc.Space(h=10)
    ]


def device_popup(deployment, color):
    start = pretty_date(deployment.period_start)
    end = pretty_date(deployment.period_end) if deployment.period_end else "-"
    return dmc.Container([
        *header(deployment.id, deployment.node_type, deployment.node_label, color),
        *time_section("Start", start, "End", end),
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
    created_at = pretty_date(environment.created_at)
    updated_at = pretty_date(environment.updated_at) if environment.updated_at else "-"
    return dmc.Container([
        *header(environment.id, "Environment Data Point", "", "#abde00"),
        *time_section("Created", created_at, "Updated", updated_at),
    ],
        fluid=True,
        style={"width": "240px"}
    )


def note_popup(note):
    created_at = pretty_date(note.created_at) if note.created_at else "-"
    updated_at = pretty_date(note.updated_at) if note.updated_at else "-"
    return dmc.Container([
        *header(note.id, "Note", note.node_label, "#ffd800"),
        *time_section("Created", created_at, "Updated", updated_at),
        dmc.Space(h=10),
        dmc.Group(
            children=[dmc.Badge(t, size="sm", variant="outline") for t in note.tags],
            spacing="xs"
        ),
    ],
        fluid=True,
        style={"width": "220px"}
    )
