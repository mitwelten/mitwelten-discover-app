import dash_mantine_components as dmc
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.components.button.components.action_button import action_button
from dashboard.config.id import *
from dashboard.model.note import Note
from dashboard.util.user_validation import get_user_from_cookies
from dashboard.util.util import pretty_date


def list_item(text, icon):
    return dmc.ListItem(
        text,
        icon=dmc.ThemeIcon(
            DashIconify(icon=icon, width=16),
            radius="xl",
            color=PRIMARY_COLOR,
            size=24,
        ),
    )


def note_detail_view(note: Note):
    user = get_user_from_cookies()
    return [dmc.Grid([
        dmc.Col(dmc.Title(note.title, order=5), span="content"),
        dmc.Col(dmc.Group([
            action_button(ID_NOTE_ATTACHMENT_BUTTON, "material-symbols:attach-file"),
            action_button(ID_NOTE_EDIT_BUTTON, "material-symbols:edit", disabled=True if user is None else False)
        ]),
            span="content"
        ),
    ],
        justify="space-between"
    ),
        dmc.Grid([
            dmc.Col(dmc.Text(f"{note.creator} • {pretty_date(note.created_at)}", size="xs", color="dimmed"), span="content"),
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(dmc.Divider(size="xs")),
            dmc.Col(
                dmc.Spoiler(
                    note.description,
                    showLabel="Show more",
                    hideLabel="Hide",
                    maxHeight=250,
                ),
                span=12
            ),
        ])
    ]
