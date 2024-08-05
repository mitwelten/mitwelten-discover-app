import dash_mantine_components as dmc
from dash_iconify import DashIconify

from src.config.app_config import PRIMARY_COLOR


def action_button(button_id = None, icon: str = "", size="lg", disabled=False, variant="filled"):
    return dmc.ActionIcon(
        DashIconify(
            icon=icon,
            width=20 if size == "lg" else 16,
            color=PRIMARY_COLOR,
        ),
        disabled=disabled,
        variant=variant,
        size=size,
        id=button_id if button_id else "",
        n_clicks=0,
        radius="xl",
        style={"zIndex":100},

    )
