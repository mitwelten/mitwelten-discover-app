from dashboard.api.api_client import get_fake_note_by_id
from dashboard.model.note import Note


def create_note_form(trigger_id, theme):
    note = get_fake_note_by_id(trigger_id)
    note = Note(note)

