from dash.dash import flask
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

info_dialog = dmc.Modal(
            id=ID_INFO_DIALOG_MODAL,
            title=dmc.Title("Welcome to the web map Discover of the Mitwelten project!"),
            zIndex=1000000,
            centered=True,
            size="xl",
            withCloseButton=False,
            opened=False,
            children=[
                dmc.Text(DISCOVER_DESCRIPTION, size="sm"),
                dmc.Space(h=10),
                dmc.Group([
                    dmc.Text("For more information visit:", size="sm"),
                    dmc.Anchor("mitwelten.org", href="https://mitwelten.org", target="_blank", size="sm"),
                    ], spacing="xs"),
                dmc.Space(h=40),
                dmc.ScrollArea([
                    deployment_info,
                    #dmc.Button(id="tour")
                    ]),
                dmc.Group([
                    dmc.Button(
                        id="id-info-modal-close-button", 
                        children=dmc.Text("Close")
                        ),
                    ], position="right"
                )],
        )


login_button = dmc.Anchor(
    action_button(button_id="", icon="material-symbols:login"),
    id=ID_LOGIN_BUTTON_HREF,
    href=f"{DOMAIN_NAME}/login?lat=47.52&lon=7.61"
)

def create_avatar(user):
    return dmc.HoverCard([
        dmc.HoverCardTarget(dmc.Avatar(user.initials, size="md", radius="xl")),
        dmc.HoverCardDropdown([
            dmc.Stack([
                dmc.Avatar(user.initials, size="60px", radius="xl", color=PRIMARY_COLOR, variant="filled"),
                dmc.Text(user.full_name),
                dmc.Text(user.username, color="dimmed"),
                dmc.Divider(size="md", color="black"),
                dmc.Anchor(
                    dmc.Button(
                        "Logout",
                        rightIcon=DashIconify(icon="material-symbols:logout"),
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
        transition="scale-y",
        transitionDuration=100,
        position="bottom-end",
        withArrow=True,
        arrowSize=10,
        arrowOffset=15,
        zIndex=500000,
        styles={"display": "none"}
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
            login_button,
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
            action_button(button_id=ID_INFO_DIALOG_BUTTON, icon="material-symbols:info-i"),
            info_dialog
        ],
            id=ID_FAB_CONTAINER
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
        return no_update, hidden, visible 
    return create_avatar(user), visible, hidden


def notify(notification):
    return [no_update, notification, no_update, no_update, no_update, no_update, no_update]


@app.callback(
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Output(ID_NOTIFICATION, "children", allow_duplicate=True),
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Input(ID_ADD_NOTE_BUTTON, "n_clicks"),
    State(ID_BROWSER_PROPERTIES_STORE, "data"),
    State(ID_SETTINGS_DRAWER, "opened"),
    State(ID_SETTINGS_DRAWER, "size"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_MAP, "bounds"),
    State(ID_MAP, "center"),
    State(ID_TAG_DATA_STORE, "data"),
    State(ID_APP_THEME, "theme"),
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
        theme
):
    if click is None or click == 0:
        raise PreventUpdate

    user = get_user_from_cookies()

    if user is None:
        return notify(notification("Log in to create notes!", NotificationType.NOT_PERMITTED))
    
    new_note = Note(empty_note)

    # initially the bounds of the map are None
    print("Bounds: ", bounds)
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
    new_note["id"] = new_note["note_id"]
    new_note["author"] = user.full_name

    notes = dict(entires=[])
    view = note_view(Note(new_note), theme, True, all_tags["all"])

    return notes, no_update, dict(data=new_note, new=True), view, True, CHART_DRAWER_HEIGHT, False 

