import dash_mantine_components as dmc

from dashboard.components.button.components.action_button import action_button
from dashboard.config.id import *


def control_buttons():
    return [
        action_button(button_id=ID_OPEN_LEFT_DRAWER_BUTTON, icon="material-symbols:menu"),
        dmc.MediaQuery(
            action_button(button_id=ID_BOTTOM_DRAWER_BUTTON, icon="material-symbols:layers-outline"),
            largerThan="sm",
            styles={"visibility": "hidden"}
        )
    ]
