import dash_mantine_components as dmc
from dash import html


from src.config.map_config import get_source_props
from src.model.note import Note
from src.util.util import apply_newlines, local_formatted_date


def header(source_type, title=None):
    return [
            html.Div([
                dmc.Text(
                    get_source_props(source_type)["name"] if title is None else title, 
                    weight=700,
                    size="xs", 
                    className="note-marker-title"
                    ),
                dmc.Image(src=get_source_props(source_type)["marker"], width="16px"),
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'start'
                    }),
        dmc.Space(h=10),
        dmc.Divider(),
        dmc.Space(h=10),
    ]


def details(fst_label, fst_time, snd_label=None, snd_time=None):
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


def device_popup(deployment, timezone):
    start = local_formatted_date(deployment.period_start, timezone)
    end   = local_formatted_date(deployment.period_end, timezone) if deployment.period_end else "-"
    return dmc.Container([
        *header(deployment.node_type),
        *details("Start", start, "End", end),
    ],
        fluid=True,
        style={"width": "240px", "padding": "0px", "height": "75px"}
    )


def environment_popup(environment, timezone):
    created_at = local_formatted_date(environment.created_at, timezone)
    updated_at = local_formatted_date(environment.updated_at, timezone) if environment.updated_at else "-"
    return dmc.Container([
        *header("Environment"),
        *details("Created", created_at, "Updated", updated_at),
    ],
        fluid=True,
        style={"width": "240px", "padding": "0px", "height": "75px"}
    )

def note_popup(note: Note, timezone):
    created_at = local_formatted_date(note.date, timezone)
    if note.description is not None:
        description = (note.description[:75] + '...') if len(note.description) > 75 else note.description
    else:
        description = "-"

    return dmc.Container([
        html.Div(header("Note", note.title)),
        html.Div(
            dmc.Text(apply_newlines(description), lineClamp=3, size="xs"),
            style={"maxHeight":"70px", "overflow": "hidden"}
            ),
        dmc.Text(created_at, color="dimmed", size="xs"),
        ],
        fluid=True,
        style={"width": "220px", "maxHeight": "144px", "overflow": "hidden", "padding": "0px"},
    )
