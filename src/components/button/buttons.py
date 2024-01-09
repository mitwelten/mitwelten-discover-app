import dash_mantine_components as dmc
from dash import Output, Input, html
from dash_iconify import DashIconify

from configuration import DOMAIN_NAME, PRIMARY_COLOR
from src.components.button.components.action_button import action_button
from src.components.map.layer_selection.drawer import map_menu_drawer
from src.components.map.layer_selection.popup import map_menu_popup
from src.config.id_config import *
from src.main import app
from src.util.user_validation import get_user_from_cookies

login_button = dmc.Anchor(
    action_button(button_id="id-login-btn", icon="material-symbols:login"),
    href=f"{DOMAIN_NAME}/login"
)


def create_avatar(user):
    return dmc.HoverCard([
        dmc.HoverCardTarget(dmc.Avatar(user.initials, size="md", radius="xl")),
        dmc.HoverCardDropdown([
            dmc.Stack([
                dmc.Avatar(user.initials, size="60px", radius="xl", color=PRIMARY_COLOR),
                dmc.Text(user.full_name),
                dmc.Text(user.username, color="dimmed"),
                dmc.Divider(size="md", color="black"),
                dmc.Anchor(
                    dmc.Button(
                        "Logout",
                        rightIcon=DashIconify(icon="material-symbols:logout"),
                        variant="light",
                        fullWidth=True,
                    ),
                    href="/logout",
                    refresh=True
                )
            ],
                align="center"
            )
        ])
    ],
        transition="scale-y",
        transitionDuration=100,
        position="bottom-end",
        withArrow=True,
        arrowSize=10,
        arrowOffset=15,
        zIndex=500000
    )


control_buttons = [
        action_button(
            button_id=ID_OPEN_SETTINGS_DRAWER_BUTTON,
            icon="material-symbols:menu"
        ),
        dmc.Group([
            html.Div(
                id=ID_LOGIN_AVATAR_CONTAINER
            ),
            action_button(button_id=ID_ADD_NOTE_BUTTON, icon="material-symbols:add-comment-outline"),
            dmc.MediaQuery([
                action_button(button_id=ID_BOTTOM_DRAWER_BUTTON, icon="material-symbols:layers-outline"),
                dmc.Drawer(
                    map_menu_drawer("drawer"),
                    id=ID_MAP_LAYER_BOTTOM_DRAWER,
                    size="lg",
                    zIndex=90000,
                    position="bottom",
                    withOverlay=True,
                    closeOnClickOutside=True
                )
            ],
                largerThan="sm",
                styles={"display": "none"}
            ),
            dmc.MediaQuery(
                map_menu_popup("menu"),
                smallerThan="sm",
                styles={"display": "none"}
            ),

        ],
            id=ID_FAB_CONTAINER
        )
    ]


@app.callback(
    Output(ID_LOGIN_AVATAR_CONTAINER, "children"),
    Input(ID_LOGIN_AVATAR_CONTAINER, "n_clicks"),
)
def login(_):
    user = get_user_from_cookies()
    if user is None:
        return login_button
    return create_avatar(user)
