from dash.dash import flask
import dash_mantine_components as dmc
from dash import Output, Input, html, State, no_update, dcc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from werkzeug.datastructures import auth
from src.api.api_note import create_note

import json
from datetime import datetime
from pprint import pprint
from configuration import DOMAIN_NAME, PRIMARY_COLOR
from src.components.button.components.action_button import action_button
from src.components.map.layer_selection.drawer import map_menu_drawer
from src.components.map.layer_selection.popup import map_menu_popup
from src.config.id_config import *
from src.main import app
from src.model.note import Note, empty_note
from src.util.user_validation import get_user_from_cookies
from src.components.data_drawer.types.note.form_view import note_form_view

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


@app.callback(
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Output(ID_ALERT_INFO, "is_open", allow_duplicate=True),
    Output(ID_ALERT_INFO, "children", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Input(ID_ADD_NOTE_BUTTON, "n_clicks"),
    State(ID_BROWSER_PROPERTIES_STORE, "data"),
    State(ID_SETTINGS_DRAWER, "opened"),
    State(ID_SETTINGS_DRAWER, "size"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_MAP, "bounds"),
    State(ID_TAG_DATA_STORE, "data"),
    prevent_initial_call=True
)
def create_note_on_map(
        click,
        browser_props,
        drawer_state,
        settings_drawer_size,
        data_drawer_size,
        bounds,
        all_tags
):
    if click is None or click == 0:
        raise PreventUpdate

    user = get_user_from_cookies()

    if user is None:
        notification = [
            dmc.Title("Operation not permitted", order=6),
            dmc.Text("Log in to create notes!")
        ]
        return no_update, True, notification
    
    new_note = Note(empty_note)

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
    new_note.date = datetime.now().isoformat()

    auth_cookie = flask.request.cookies.get("auth")
    res = create_note(new_note, auth_cookie)
    new_note = json.loads(res.content)
    new_note["id"] = new_note["note_id"]
    notes = dict(entires=[])

    return notes, no_update, no_update, dict(data=new_note), note_form_view(Note(new_note), all_tags), 650, True

