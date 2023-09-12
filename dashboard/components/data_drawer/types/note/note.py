import dash_mantine_components as dmc
from dash import html, dcc

from dashboard.components.button.components.action_button import action_button
from dashboard.components.data_drawer.types.note import form_callbacks, attachment_callbacks, callbacks
from dashboard.components.data_drawer.types.note.detail_view import note_detail_view
from dashboard.components.data_drawer.types.note.form_view import note_form


from dashboard.config.id import *
from dashboard.config.id import ID_NOTE_DRAWER_TITLE, ID_NOTE_DETAIL_VIEW, ID_NOTE_FORM_VIEW
from dashboard.model.note import Note
from dashboard.util.user_validation import get_user_from_cookies

from dash import Output, Input
from dash.exceptions import PreventUpdate

from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note


def create_note_view():
    return dmc.Container([
        dmc.Title(id=ID_NOTE_DRAWER_TITLE, order=5),
        html.Div(id=ID_NOTE_DETAIL_VIEW),
        html.Div(id="id-test"),
        html.Div(id=ID_NOTE_FORM_VIEW, style={"display": "none"})
    ])


@app.callback(
    Output("id-test", "children"),
    Input(ID_SELECTED_NOTE_STORE, "data"),
)
def update_content_from_store(selected_note):
    print("callback: common html element - edit Mode", selected_note["inEditMode"])
    if selected_note is None:
        raise PreventUpdate
    note = Note(selected_note["data"])
    if selected_note.get("inEditMode", False):
        return note_form(note)
    return note_detail_view(note)
