from datetime import datetime

import dash
from dash import Output, Input, State
from dash.exceptions import PreventUpdate

from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note, empty_note
from dashboard.util.user_validation import get_user_from_cookies


@app.callback(
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_NOTE_EDIT_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def add_note_form_view_to_drawer_container(click):
    if click is None or click == 0:
        raise PreventUpdate
    return dict(state=True)


@app.callback(
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    Input(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "submit_n_clicks"),
    prevent_initial_call=True
)
def add_note_detail_view_to_drawer_container(save_click, cancel_click):
    if save_click is None or save_click == 0:
        if cancel_click is None or cancel_click == 0:
            raise PreventUpdate
    return dict(state=False)


@app.callback(
    Output(ID_NEW_NOTE_STORE, "data"),
    Output(ID_SELECTED_MARKER_STORE, "data", allow_duplicate=True),
    Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_MAP, "dbl_click_lat_lng"),
    prevent_initial_call=True
)
def handle_double_click(click):
    user = get_user_from_cookies()
    if user is None:
        notification = create_notification(
            "Operation not permitted",
            "Log in to create notes!",
            NotificationType.WARN
        )
        return dash.no_update, dash.no_update, notification, dict(state=True)

    new_note = Note(empty_note)
    new_note.lat = click[0]
    new_note.lon = click[1]
    new_note.creator = user.full_name
    new_note.created_at = datetime.now().isoformat()
    new_note.updated_at = datetime.now().isoformat()
    new_note = new_note.to_dict()
    return new_note, dict(data=new_note, type="Notes"), dash.no_update, False, False, False, False, dict(state=False)





# @app.callback(
#     Output(ID_NOTIFICATION_CONTAINER, "children"),
#     Input({"role": "note-save-button", "id": ALL}, "n_clicks"),
#     prevent_initial_call=True
# )
# def save_edited_note(click):
#     click = safe_reduce(lambda x, y: x + y, click)
#     if click is not None:
#         return create_notification(
#             "Save Note",
#             "Operation under construction",
#             NotificationType.ERROR,
#             "material-symbols:construction"
#         )
#     return dash.no_update



