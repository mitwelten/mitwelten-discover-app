import dash_mantine_components as dmc
from dash import html, dcc, State

from dashboard.components.data_drawer.types.note import form_callbacks, attachment_callbacks, callbacks
from dashboard.components.data_drawer.types.note.detail_view import note_detail_view
from dashboard.components.data_drawer.types.note.form_view import note_form

from dash import Output, Input
from dash.exceptions import PreventUpdate

from dashboard.config.id_config import *
from dashboard.maindash import app
from dashboard.model.note import Note


def create_note_view(note_label):
    return dmc.Container([
        dcc.Store(id=ID_VISIBLE_NOTE_VIEW_STORE, data=dict(currentView=None)),
        dmc.Text(f"Note - {note_label}", weight=500),
        dmc.Title(id=ID_NOTE_DRAWER_TITLE, order=5),
        html.Div(id=ID_NOTE_VIEW, style={}),
    ],
        size="md"
    )


@app.callback(
    Output(ID_NOTE_VIEW, "children"),
    Output(ID_VISIBLE_NOTE_VIEW_STORE, "data"),
    Input(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_VISIBLE_NOTE_VIEW_STORE, "data"),
)
def update_content_from_store(selected_note, view):
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

    is_edit_mode = selected_note.get("inEditMode", False)
    current_view = view["currentView"]
    note = Note(selected_note["data"])

    if not is_edit_mode and current_view == "detail":
        raise PreventUpdate
    if is_edit_mode and current_view == "edit":
        raise PreventUpdate
    if is_edit_mode:
        return note_form(note), dict(currentView="edit")
    else:
        return note_detail_view(note), dict(currentView="detail")
