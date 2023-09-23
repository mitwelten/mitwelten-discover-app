import dash
import dash_mantine_components as dmc
import flask
from dash import html, Output, Input, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.api.api_note import delete_note
from dashboard.components.button.components.action_button import action_button
from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id_config import *
from dashboard.model.note import Note
from dashboard.util.user_validation import get_user_from_cookies
from dashboard.util.util import pretty_date
from dashboard.maindash import app


def list_item(text, icon):
    return dmc.ListItem(
        text,
        icon=dmc.ThemeIcon(
            DashIconify(icon=icon, width=16),
            radius="xl",
            color=PRIMARY_COLOR,
            size=24,
        ),
    )


def note_detail_view(note: Note):
    user = get_user_from_cookies()
    icon_private = DashIconify(icon="material-symbols:lock",                    width=14, color="#868e96", style={"display":"block", "marginLeft":"3px"})
    icon_public  = DashIconify(icon="material-symbols:lock-open-right-outline", width=14, color="#868e96", style={"display":"block", "marginLeft":"3px"})
    return [dmc.Grid([
        dmc.Col(dmc.Title(note.title, order=5), span="content"),
        dmc.Col(dmc.Group([
            action_button(ID_NOTE_ATTACHMENT_BUTTON, "material-symbols:attach-file"),
            action_button(ID_NOTE_DELETE_BUTTON, "material-symbols:delete") if user is not None else {},
            action_button(ID_NOTE_EDIT_BUTTON, "material-symbols:edit", disabled=True if user is None else False)
        ]),
            span="content"
        ),
    ],
        justify="space-between"
    ),
        dmc.Grid([
            dmc.Col(
                html.Span([
                    dmc.Text(
                        f"{note.author} • {pretty_date(note.date)} •",
                        size="xs",
                        color="dimmed",
                        style={"display":"block"},
                    ),
                    dmc.Text(icon_public if note.public else icon_private),
                ],
                    style={"display":"inline-flex"}
                ),
                span="content"),
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(dmc.Divider(size="xs")),
            dmc.Col(
                dmc.Spoiler(
                    note.description,
                    showLabel="Show more",
                    hideLabel="Hide",
                    maxHeight=250,
                ),
                span=12
            ),
        ])
    ]
@app.callback(
    Output(ID_CONFIRM_DELETE_DIALOG, "displayed", allow_duplicate=True),
    Input(ID_NOTE_DELETE_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def map_click(click):
    if click == 0 or click is None:
        raise PreventUpdate
    return True


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
    Input(ID_CONFIRM_DELETE_DIALOG, "submit_n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def deactivate_edit_mode(delete_click, note):
    if delete_click is None or delete_click == 0:
        raise PreventUpdate

    auth_cookie = flask.request.cookies.get("auth")
    success = delete_note(note["data"]["id"], auth_cookie)
    if not success:
        notification = create_notification(
            "Operation not permitted",
            "Log in to delete notes!",
            NotificationType.ERROR
        )
        return dash.no_update, dash.no_update, notification

    return dict(data=None, inEditMode=False), False, dash.no_update
