from enum import Enum

import dash_mantine_components as dmc
from dash_iconify import DashIconify


class NotificationType(Enum):
    INFO = "material-symbols:circle-notifications",
    WARN = "",
    ERROR = ""


def create_notification(title, message, type: NotificationType, icon = None):
    if icon is None:
        match type:
            case NotificationType.WARN:
                icon = "material-symbols:warning-outline-rounded"
            case NotificationType.ERROR:
                icon = "material-symbols:error-outline-rounded"
            case _:
                icon = "material-symbols:circle-notifications"

    return dmc.Notification(
        title=title,
        id=f"id-notification-{title}",
        action="show",
        message=message,
        icon=DashIconify(icon=icon, height=24)
    )
