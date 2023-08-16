import dash
import dash_mantine_components as dmc
from dash import Output, Input, ALL, State

from dashboard.api.api_client import get_fake_note_by_id
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note


def create_note_form(trigger_id, theme):
    note = get_fake_note_by_id(trigger_id)
    note = Note(note)
    return dmc.Text(f"Form of: {note}")


def create_form(note):
    return dmc.Text(f"Form of: {note}")
