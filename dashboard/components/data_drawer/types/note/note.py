import dash_mantine_components as dmc
from dash import html, dcc

from dashboard.components.button.components.action_button import action_button
from dashboard.components.data_drawer.types.note import form_callbacks, attachment_callbacks, callbacks

from dashboard.config.id import *
from dashboard.model.note import Note
from dashboard.util.user_validation import get_user_from_cookies


def drawer_content(note: Note):
    note_dict = note.to_dict()
    user = get_user_from_cookies()
    return dmc.Container([
            dcc.Store(ID_CURRENT_NOTE_STORE, data=dict(note_dict), storage_type="local"),
            dcc.Store({"role": "Notes", "id": note.note_id, "label": "Prevent Marker Event"}, data=dict(state=False), storage_type="local"),
            dmc.Grid([
                dmc.Col(dmc.Title(id=ID_NOTE_DRAWER_TITLE, order=5), span="content"),
                dmc.Col(dmc.Group([
                    action_button(ID_NOTE_ATTACHMENT_BUTTON, "material-symbols:attach-file"),
                    action_button(ID_NOTE_EDIT_BUTTON, "material-symbols:edit", disabled=True if user is None else False)
                ]),
                    span="content"
                ),
            ],
                justify="space-between",
            ),
            html.Div(id=ID_NOTE_DETAIL_VIEW),
            html.Div(id=ID_NOTE_FORM_VIEW, style={"display": "none"})
        ]),


def create_note_view(notes, note_id, _):
    for note in notes:
        if note["note_id"] == note_id:
            return drawer_content(Note(note))

