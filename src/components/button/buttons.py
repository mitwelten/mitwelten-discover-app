from dash.dash import flask
from src.config.app_config import CHART_DRAWER_HEIGHT, PRIMARY_COLOR
import dash_mantine_components as dmc
from dash import Output, Input, html, State, no_update, ctx
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from src.components.notification.notification import NotificationType, notification
from src.api.api_note import create_note

import json
from datetime import datetime, timezone
from configuration import DOMAIN_NAME
from src.components.button.components.action_button import action_button
from src.components.map.layer_selection.drawer import map_menu_drawer
from src.components.map.layer_selection.popup import map_menu_popup
from src.config.app_config import CHART_DRAWER_HEIGHT, PRIMARY_COLOR
from src.config.id_config import *
from src.main import app
from src.model.note import Note, empty_note
from src.util.user_validation import get_user_from_cookies
from src.components.data_drawer.types.note.note_view import note_view
from src.config.app_config import DISCOVER_DESCRIPTION
from src.components.info.info import deployment_info
import logging
logger = logging.getLogger(__name__)

info_dialog = dmc.Modal(
            id=ID_INFO_DIALOG_MODAL,
            title=dmc.Title("Welcome to the web map Discover of the Mitwelten project!"),
            zIndex=1000000,
            centered=True,
            size="xl",
            withCloseButton=False,
            opened=False,
            styles={"content": {"padding": "15px"}},
            children=[
                dmc.Text(DISCOVER_DESCRIPTION, size="sm"),
                dmc.Space(h=10),
                dmc.Group([
                    dmc.Text("For more information visit:", size="sm"),
                    dmc.Anchor("mitwelten.org", href="https://mitwelten.org", target="_blank", size="sm"),
                    ], gap="xs"),
                dmc.Space(h=40),
                deployment_info,
                dmc.Flex([
                    dmc.Group([
                        dmc.Text("Found a bug?", size="sm"),
                        dmc.Anchor(
                            "Submit an issue",
                            href="https://github.com/mitwelten/mitwelten-discover-app/issues",
                            target="_blank",
                            size="sm"),
                        ]),
                    dmc.Button(
                        id="id-info-modal-close-button", 
                        children=dmc.Text("Close")
                        ),
                    ], justify="space-between")
                ],
        )


login_button = dmc.Tooltip(
        label="Login",
        children=dmc.Anchor(
            action_button(button_id="", icon="material-symbols:login"),
            id=ID_LOGIN_BUTTON_HREF,
            href=f"{DOMAIN_NAME}/login?lat=47.52&lon=7.61"
            )
        )

def create_avatar(user):
    return dmc.HoverCard([
        dmc.HoverCardTarget(dmc.Avatar(user.initials, size=35, radius="xl", color=PRIMARY_COLOR, variant="filled")),
        dmc.HoverCardDropdown([
            dmc.Stack([
                dmc.Avatar(user.initials, size="60px", radius="xl", color=PRIMARY_COLOR, variant="filled"),
                dmc.Text(user.full_name),
                dmc.Text(user.username, c="dimmed"),
                dmc.Divider(size="md", color="black"),
                dmc.Anchor(
                    dmc.Button(
                        "Logout",
                        rightSection=DashIconify(
                            icon="material-symbols:logout"
                            ),
                        variant="filled",
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

        transitionProps={"transition": "scale-y", "duration": 100},
        position="bottom-end",
        withArrow=True,
        arrowSize=10,
        arrowOffset=15,
        zIndex=500000,
        styles={"display": "none"}
    )

settings_button= dmc.ActionIcon(
                DashIconify(
                    icon="material-symbols:menu",
                    width=20,
                    color=PRIMARY_COLOR,
                    ),
                size="lg",
                id=ID_OPEN_SETTINGS_DRAWER_BUTTON,
                radius="xl",
                style={"position": "absolute", "top": 20, "left": 20, "zIndex":100},
                )

add_note_button = dmc.Tooltip(
        label="Add a new Note",
        children=action_button(
            button_id=ID_ADD_NOTE_BUTTON, 
            icon="material-symbols:add-comment-outline"
            )
        )
map_selection_bottom_drawer_button = dmc.Tooltip(
        label="Select map layers",
        hiddenFrom="sm",
        children=dmc.ActionIcon(
                DashIconify(
                    icon="material-symbols:layers-outline",
                    width=20,
                    color=PRIMARY_COLOR,
                    ),
                size="lg",
                id=ID_BOTTOM_DRAWER_BUTTON,
                n_clicks=0,
                radius="xl",
                style={"zIndex":100},
                hiddenFrom="sm"
                )
        )

floating_buttons = [
        settings_button,
        dmc.Group(
            gap="xs",
            id=ID_FAB_CONTAINER,
            children=[
                html.Div(id=ID_LOGIN_AVATAR_CONTAINER),
                login_button,
                add_note_button,
                map_selection_bottom_drawer_button,
                dmc.Drawer(
                    map_menu_drawer("drawer"),
                    id=ID_MAP_LAYER_BOTTOM_DRAWER,
                    size=400,
                    zIndex=90000,
                    position="bottom",
                    withOverlay=True,
                    closeOnClickOutside=True,
                    hiddenFrom="sm",
                    ),
                map_menu_popup("menu"),
                dmc.Tooltip(
                    label="More Information",
                    children=action_button(button_id=ID_INFO_DIALOG_BUTTON, icon="material-symbols:info-i")
                    ),
                info_dialog
                ]
            )
        ]

@app.callback(
        Output(ID_INFO_DIALOG_MODAL, "opened"),
        Input(ID_INFO_DIALOG_BUTTON, "n_clicks"),
        Input("id-info-modal-close-button", "n_clicks"),
        prevent_initial_call=True
)
def open_info_dialog(click, close_click):
    if ctx.triggered_id == ID_INFO_DIALOG_BUTTON:
        return True
    return False

@app.callback(
    Output(ID_LOGIN_AVATAR_CONTAINER, "children"),
    Output(ID_LOGIN_AVATAR_CONTAINER, "style"),
    Output(ID_LOGIN_BUTTON_HREF, "style"),
    Input(ID_LOGIN_AVATAR_CONTAINER, "n_clicks"),
)
def login(_):
    user = get_user_from_cookies()
    visible = {"display": "block"}
    hidden  = {"display": "none"}
    if user is None:
        logger.debug("No user logged in")
        return no_update, hidden, visible 

    logger.info("User is logged in")
    return create_avatar(user), visible, hidden


def notify(notification):
    return [no_update, notification, no_update, no_update, no_update]


@app.callback(
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Output(ID_NOTIFICATION, "children", allow_duplicate=True),
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Input(ID_ADD_NOTE_BUTTON, "n_clicks"),
    State(ID_BROWSER_PROPERTIES_STORE, "data"),
    State(ID_SETTINGS_DRAWER, "opened"),
    State(ID_SETTINGS_DRAWER, "size"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_MAP, "bounds"),
    State(ID_MAP, "center"),
    State(ID_TAG_DATA_STORE, "data"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_TIMEZONE_STORE, "data"),
    State(ID_APP_THEME, "forceColorScheme"),
    prevent_initial_call=True
)
def create_note_on_map(
        click,
        browser_props,
        drawer_state,
        settings_drawer_size,
        data_drawer_size,
        bounds,
        center,
        all_tags,
        all_notes,
        tz,
        theme
):
    if click is None or click == 0:
        raise PreventUpdate
    if ctx.triggered_id is None:
        raise PreventUpdate

    user = get_user_from_cookies()

    if user is None:
        return notify(notification("Log in to create notes!", NotificationType.NOT_PERMITTED))
    
    new_note = Note(empty_note)

    # initially the bounds of the map are None
    if bounds is not None:
        top    = bounds[1][0]
        bottom = bounds[0][0]
        left   = bounds[0][1]
        right  = bounds[1][1]

        # visibile map distance in grad
        map_delta_lat = top - bottom
        map_delta_lon = right - left

        # set drawer size to 1 if the settings drawer is closed
        settings_drawer_size = 0 if not drawer_state else settings_drawer_size

        # the height of the data drawer in grad
        data_drawer_height = map_delta_lat   / browser_props["height"] * data_drawer_size

        # the width of the settings drawer in grad
        settings_drawer_width = map_delta_lon / browser_props["width"]  * settings_drawer_size

        new_note.lon = left + settings_drawer_width + ((map_delta_lon - settings_drawer_width) / 2)
        new_note.lat = bottom + data_drawer_height + ((map_delta_lat - data_drawer_height) / 2)
    else:
        new_note.lat = center[0]
        new_note.lon = center[1]

    new_note.date = datetime.now(timezone.utc).isoformat()
    new_note.public = True

    auth_cookie = flask.request.cookies.get("auth")
    res = create_note(new_note, auth_cookie)

    if res.status_code != 200:
        return notify(notification(f"Could not create Note - {res.status_code}", NotificationType.WENT_WRONG))

    new_note = json.loads(res.content)
    new_note = Note(new_note)
    new_note.author = user.full_name

    view = note_view(new_note, theme, tz["tz"], True, all_tags["all"])
    all_notes["entries"].append(new_note.to_dict())

    return all_notes, no_update, dict(data=new_note.to_dict()), view, True

