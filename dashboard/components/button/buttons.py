import dash_mantine_components as dmc
import flask
import jwt
from dash import Output, Input, State
from dash_iconify import DashIconify

from dashboard.components.button.components.action_button import action_button
from dashboard.components.map.layer_selection.drawer import map_menu_drawer
from dashboard.components.map.layer_selection.popup import map_menu_popup
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.user import User

login_button = dmc.Anchor(
    action_button(button_id="id-login-btn", icon="material-symbols:login"),
    href="http://localhost:8000/login"
)


def create_avatar(user):
    return dmc.HoverCard([
        dmc.HoverCardTarget(dmc.Avatar(user.initials, size="md", radius="xl")),
        dmc.HoverCardDropdown([
            dmc.Stack([
                dmc.Avatar(user.initials, size="60px", radius="xl", color="mitwelten_green"),
                dmc.Text(user.full_name),
                dmc.Text(user.username, color="dimmed"),
                dmc.Divider(size="md", color="black"),
                dmc.Button(
                    "Logout",
                    rightIcon=DashIconify(icon="material-symbols:logout"),
                    variant="light",
                    fullWidth=True,
                ),
            ],
                align="center"
            )
        ],
        )
    ],
        transition="scale-y",
        transitionDuration=100,
        position="bottom-end",
        withArrow=True,
        arrowSize=10,
        arrowOffset=15,
        zIndex=500000
    )


def control_buttons():
    return [
        action_button(button_id=ID_OPEN_LEFT_DRAWER_BUTTON, icon="material-symbols:menu"),
        dmc.Group([
            dmc.MediaQuery([
                action_button(button_id=ID_BOTTOM_DRAWER_BUTTON, icon="material-symbols:layers-outline"),
                dmc.Drawer(
                    map_menu_drawer("drawer"),
                    id=ID_MAP_LAYER_BOTTOM_DRAWER,
                    size="lg",
                    zIndex=90000,
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
            id="login-avatar-container"
        )
    ]


@app.callback(
    Output("login-avatar-container", "children"),
    Input("login-avatar-container", "n_clicks"),
    State("login-avatar-container", "children")
)
def login(_, children):

    cookies = flask.request.cookies
    try:
        decoded_cookie = jwt.decode(
            cookies.get("auth"), options={"verify_signature": False}
        )
        user = User(decoded_cookie)

    except Exception as e:
        print("No user found!")
        return [login_button, *children]
    return [create_avatar(user), *children]

