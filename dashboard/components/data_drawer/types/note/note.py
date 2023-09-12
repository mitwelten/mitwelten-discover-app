import dash_mantine_components as dmc
from dash import html, dcc, State

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
        dcc.Store(id="id-visible-view", data=dict(currentView=None)),
        dmc.Title(id=ID_NOTE_DRAWER_TITLE, order=5),
        html.Div(id="id-test"),
    ])


@app.callback(
    Output("id-test", "children"),
    Output("id-visible-view", "data"),
    Input(ID_SELECTED_NOTE_STORE, "data"),
    State("id-visible-view", "data"),
)
def update_content_from_store(selected_note, view):
    print("callback: common html element - edit Mode", selected_note["inEditMode"])
    if selected_note is None:
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
