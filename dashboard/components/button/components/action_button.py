import dash_mantine_components as dmc
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR


def action_button(button_id: str = None, icon: str = None, size="lg"):
    return dmc.ActionIcon(
        DashIconify(
            icon=icon,
            width=20 if size == "lg" else 16,
            color=PRIMARY_COLOR,
        ),
        variant="light",
        size=size,
        id=button_id if button_id else "",
        n_clicks=0,
        radius="xl",
    )
