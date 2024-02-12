import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from src.components.data_drawer.types.note.form_callbacks import load_callbacks

from src.components.button.components.action_button import action_button
from src.components.data_drawer.types.note.attachment import attachment_modal
from src.components.data_drawer.types.note.detail_view import note_detail_view
from src.components.data_drawer.types.note.form_view import note_form
from src.config.id_config import *
from src.model.note import Note
from src.util.user_validation import get_user_from_cookies



def create_note_content(selected_note, all_tags):
    load_callbacks()
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

    is_edit_mode = selected_note.get("inEditMode", False)
    note = Note(selected_note["data"])
    if is_edit_mode:
        children = note_form(note, all_tags)
    else:
        children = note_detail_view(note)

    return note_container(selected_note, children)


def get_form_controls(public = False):
    return [
        dmc.Switch(
            id=ID_NOTE_EDIT_PUBLIC_FLAG,
            offLabel=DashIconify(icon="material-symbols:lock", width=15),
            onLabel=DashIconify(icon="material-symbols:lock-open-right-outline", width=15),
            size="sm",
            checked=public
        ),
        action_button(button_id=ID_LOCATION_MODAL_BUTTON, icon="material-symbols:edit-location-alt-outline-sharp"),
    ]


def get_view_controls(user):
    return [
        action_button(
            button_id=ID_NOTE_EDIT_BUTTON,   
            icon="material-symbols:edit", 
            disabled=True if user is None else False),
        action_button(button_id=ID_NOTE_DELETE_BUTTON, icon="material-symbols:delete") if user is not None else {}
    ]


def note_container(selected_note, children):
    editable = selected_note.get("inEditMode", False)
    note = Note(selected_note["data"])
    user = get_user_from_cookies()
    title    = "Create / Edit Note"           if editable else note.title
    controls = get_form_controls(note.public) if editable else get_view_controls(user)
    controls.append(action_button(ID_NOTE_ATTACHMENT_BUTTON, "material-symbols:attach-file"))

    return dmc.Container([

        dmc.Grid([
            dmc.Col(dmc.Title(title),span="content"),
            dmc.Col(dmc.Group(controls, spacing="sm"),
                span="content"
            )
        ],
            justify="space-between"
        ),
        *children,
        attachment_modal(selected_note)
    ])