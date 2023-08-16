import dash
import dash_leaflet as dl
from dash import Output, Input, State, html, dcc

import dash_mantine_components as dmc
from dashboard.components.button.components.action_button import action_button
from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.util.user_validation import get_user_from_cookies






@app.callback(
    # Output(ID_NOTES_LAYER_GROUP, "children"),
    Output(ID_NEW_NOTE_STORE, "data"),
    Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
    Input(ID_MAP, "dbl_click_lat_lng"),
    # State(ID_NOTES_LAYER_GROUP, "children"),
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
        return dash.no_update, notification

    # marker = dl.Marker(
    #     position=[click[0], click[1]],
    #     icon=dict(iconUrl="assets/markers/note.svg", iconAnchor=[15, 6], iconSize=30),
    # )
    # if markers is None:
    #     markers = []
    # return [*markers, marker], dict(lat=click[0], lon=click[1]), dash.no_update,
    return dict(lat=click[0], lon=click[1]), dash.no_update
