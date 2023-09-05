import dash_mantine_components as dmc

from configuration import PRIMARY_COLOR
from dashboard.components.button.components.action_button import action_button
from dashboard.config.id import *
from dashboard.model.note import Note


def note_form(note: Note):
    note = Note(note)
    return [
        dmc.Grid([
            dmc.Col(dmc.Title(f"Note - {note.node_label}", order=3), span="content"),
            dmc.Col(action_button({"role": "Notes", "id": note.note_id, "label": "Attachment Store"}, "material-symbols:attach-file"), span="content"),
        ],
            justify="space-between",
        ),
        dmc.Grid([
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_TITLE, value=note.title, label="Title", variant="filled"), span=12),
            dmc.Col(dmc.Textarea(id=ID_NOTE_EDIT_DESCRIPTION, value=note.description, label="Description", variant="filled"), span=12),
            dmc.Divider(size="sm"),
            dmc.Col(dmc.TextInput(label="Latitude", value=note.lat, variant="filled"), span=6),
            dmc.Col(dmc.TextInput(label="Longitude", value=note.lon, variant="filled"), span=6),
        ]),
        dmc.Grid([
            dmc.Col(dmc.Button("Cancel", id={"role": "Notes", "id": note.note_id, "label": "Cancel Button"}, type="reset", color="gray"), span="content"),
            dmc.Col(dmc.Button("Save", id={"role": "Notes", "id": note.note_id, "label": "Save Button"}, type="submit"), span="content"),
        ],
            justify="flex-end"
        )
    ]
