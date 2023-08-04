import dash_mantine_components as dmc
from dash_iconify import DashIconify


def action_button(button_id: str = None, icon: str = None):
    return dmc.ActionIcon(
        DashIconify(
            icon=icon,
            width=20,
            color="mitwelten_green",
        ),
        variant="light",
        size="lg",
        id=button_id if button_id else "",
        n_clicks=0,
        radius="xl",
    )
