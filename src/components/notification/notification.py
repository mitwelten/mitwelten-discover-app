from enum import Enum

import dash_mantine_components as dmc
from dash_iconify import DashIconify


class NotificationType(Enum):
    WENT_WRONG    = dict(title="Something went wrong!"  , icon="material-symbols:error-outline-rounded",        color="orange"),
    SUCCESS       = dict(title="Operation Successful"   , icon="material-symbols:check-circle-outline-rounded", color="green"),
    NOT_PERMITTED = dict(title="Operation not permitted", icon="material-symbols:lock-outline",                 color="red"),
    INFO          = dict(title="Information"            , icon="material-symbols:info-outline-rounded",         color="blue"),


def notification(message: str, type: NotificationType):
    print("create notification")
    title = type.value[0]["title"]
    icon  = type.value[0]["icon"]
    color = type.value[0]["color"]

    return dmc.Notification(
         title=title,
         id=f"id-notification-{title}",
         action="show",
         message=message,
         color=color,
         icon=DashIconify(icon=icon, height=24)
     )
