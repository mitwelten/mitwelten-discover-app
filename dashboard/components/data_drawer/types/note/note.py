import dash_mantine_components as dmc
from dash import html, dcc
from dashboard.components.data_drawer.types.note import callbacks, form_callbacks, attachment_callbacks
from dashboard.components.data_drawer.types.note.detail_view import note_detail_view
from dashboard.model.note import Note
from dashboard.util.user_validation import get_user_from_cookies


def drawer_content(note):
    return dmc.Container([
        dcc.Store("id-current-note-store", data=dict(note=note), storage_type="local"),
        dcc.Store({"role": "Notes", "id": note["note_id"], "label": "Prevent Marker Event"}, data=dict(state=False)),
        html.Div(
            children=note_detail_view(note),
            id="id-note-container",
        )
    ])


def create_note_view(notes, note_id, _):
    for note in notes:
        if note["note_id"] == note_id:
            return drawer_content(note)

