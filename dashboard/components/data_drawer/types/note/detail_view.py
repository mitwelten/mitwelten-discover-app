import dash_mantine_components as dmc
from dash import Output, Input
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note
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
    return dmc.Grid([
            dmc.Col(dmc.Title(note.title, order=5), span="content"),
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(dmc.Divider(size="xs")),
            dmc.Col(
                dmc.Spoiler(
                    dmc.Text(note.description),
                    showLabel="Show more",
                    hideLabel="Hide",
                    maxHeight=50,
                ),
                span=12
            ),
            dmc.Col(dmc.Divider(size="xs")),
            dmc.Col(
                dmc.List(
                    size="md",
                    spacing="sm",
                    children=[
                        list_item(f"Creator: {note.creator}", "material-symbols:person"),
                        list_item(f"Location: {note.lat} / {note.lon}", "material-symbols:location-on-rounded"),
                        list_item(f"Created at: {pretty_date(note.created_at)}", "material-symbols:add-circle"),
                        list_item(f"Updated at: {pretty_date(note.updated_at)}", "material-symbols:edit"),
                    ],
                ),
                span="content"
            )
        ])


@app.callback(
    Output(ID_NOTE_DETAIL_VIEW, "children"),
    Input(ID_CURRENT_NOTE_STORE, "data"),
)
def update_content_from_store(data):
    note = Note(data)
    return note_detail_view(note)
