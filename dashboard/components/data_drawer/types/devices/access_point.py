from dash import Output, Input, ALL

from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app


@app.callback(
    Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
    Input({"role": "Access Point", "id": ALL, "label": "Node"}, "n_clicks"),
    prevent_initial_call=True
)
def handle_access_point_click(_):
    return create_notification(
                    "Access Point",
                    "No further data available!",
                    NotificationType.INFO)
