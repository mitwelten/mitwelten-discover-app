from datetime import datetime

import dash
from dash import Output, Input

from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note, empty_note
from dashboard.util.user_validation import get_user_from_cookies


@app.callback(
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def activate_preventing_marker_clicks(selected_note):
    return dict(state=selected_note["inEditMode"])


@app.callback(
    Output(ID_SELECTED_MARKER_STORE, "data", allow_duplicate=True),
    Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_MAP, "dbl_click_lat_lng"),
    prevent_initial_call=True
)
def handle_double_click(click_location):
    user = get_user_from_cookies()
    if user is None:
        notification = create_notification(
            "Operation not permitted",
            "Log in to create notes!",
            NotificationType.WARN
        )
        return dash.no_update, notification, dict(state=True)

    new_note = Note(empty_note)
    new_note.creator = user.full_name
    new_note.created_at = datetime.now().isoformat()
    new_note.lat = click_location[0]
    new_note.lon = click_location[1]
    new_note = new_note.to_dict()
    return dict(data=new_note, type="Note"), dash.no_update, dict(state=False)
