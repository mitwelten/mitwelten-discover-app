import dash_mantine_components as dmc
from dash import html, dcc

from dashboard.components.button.components.action_button import action_button
from dashboard.components.data_drawer.types.note import form_callbacks, attachment_callbacks, callbacks
from dashboard.components.data_drawer.types.note.detail_view import note_detail_view
from dashboard.components.data_drawer.types.note.form_view import note_form


from dashboard.config.id import *
from dashboard.model.note import Note
from dashboard.util.user_validation import get_user_from_cookies


def drawer_content():
    return dmc.Container([
            dmc.Title(id=ID_NOTE_DRAWER_TITLE, order=5),
            html.Div(id=ID_NOTE_DETAIL_VIEW),
            html.Div(id=ID_NOTE_FORM_VIEW, style={"display": "none"})
        ]),


def create_note_view(notes, note_id):
    selected_note = None
    for note in notes:
        if note["note_id"] == note_id:
            selected_note = note
    return drawer_content(), selected_note

