from pprint import pprint

import dash
import dash_mantine_components as dmc
from dash import Output, Input, State, html, dcc, ALL, MATCH
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.components.button.components.action_button import action_button
from dashboard.components.data_drawer.types.note.form_view import note_form
from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.file import File
from dashboard.model.note import Note
from dashboard.util.user_validation import get_user_from_cookies
from dashboard.util.util import pretty_date
from util.functions import safe_reduce


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
