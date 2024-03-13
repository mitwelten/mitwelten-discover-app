import dash_mantine_components as dmc
from dash import html
import time
import pytz
from datetime import datetime, timezone


from src.model.note import Note
from src.util.util import apply_newlines, local_formatted_date


def header(source_type, label, color):
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
    ]


def time_section(fst_label, fst_time, snd_label=None, snd_time=None):
    snd_date_section = None
    if snd_label is not None:
        snd_date_section = dmc.Group([
            dmc.Text(snd_label, size="xs"),
            dmc.Text(snd_time, size="xs", color="dimmed"),
        ],
            position="apart"
        )
    return [
        dmc.Group([
            dmc.Text(fst_label, size="xs"),
            dmc.Text(fst_time, size="xs", color="dimmed"),
        ],
            position="apart"
        ),
        snd_date_section if snd_date_section is not None else {},
        dmc.Space(h=10)
    ]


def device_popup(deployment, color):
    start = local_formatted_date(deployment.period_start)
    end   = local_formatted_date(deployment.period_end) if deployment.period_end else "-"
    return dmc.Container([
        *header(deployment.node_type, deployment.node_label, color),
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
    created_at = local_formatted_date(environment.created_at)
    updated_at = local_formatted_date(environment.updated_at) if environment.updated_at else "-"
    return dmc.Container([
        *header("Environment Data Point", "", "#946000"),
        *time_section("Created", created_at, "Updated", updated_at),
    ],
        fluid=True,
        style={"width": "240px"}
    )

def note_tooltip(note: Note):

    #date = local_formatted_date(note.date) if note.date else "-"
    if note.description is not None:
        description = (note.description[:75] + '..') if len(note.description) > 75 else note.description
    else:
        description = "-"

    return dmc.Container([

    html.Div([
        html.Div([
            dmc.Text(note.title, weight=700, size="sm", className="note-marker-title"),
            html.Div(className="color-point"),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'start'})
    ]),
        dmc.Space(h=5),
        dmc.Divider(),
        dmc.Space(h=5),
        html.Div(
            dmc.Text(apply_newlines(description), lineClamp=3),
            style={"maxHeight":"70px", "overflow": "hidden"}
        )
    ],
        fluid=True,
        style={"width": "220px", "maxHeight": "144px", "overflow": "hidden"},
    )

#def note_popup(note: Note):
#    return html.Div([
#        html.Div([
#            dmc.Text(note.title, weight=700, size="sm", className="note-marker-title"),
#            html.Div(className="color-point"),
#        ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'start'})
#    ],
#        #fluid=True,
#        style={"width": "150px","overflow": "hidden"},
#    )
