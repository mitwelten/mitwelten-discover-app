import dash
import dash_mantine_components as dmc
import flask
from dash import html, Output, Input, State, ALL, ctx
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from http.client import responses
from src.components.data_drawer.types.note.form_view import note_form_view
from src.components.data_drawer.types.note.attachment import attachment_area
from src.components.button.components.action_button import action_button
from configuration import PRIMARY_COLOR
from src.util.helper_functions import safe_reduce
from src.api.api_note import delete_note
from src.config.id_config import *
from src.model.note import Note
from src.util.util import pretty_date
from src.main import app
from src.util.user_validation import get_user_from_cookies


def text_to_html_list(text: str):
    children = []
    if text is not None:
        text_list = text.split("\n")
        for para in text_list:
            children.append(para)
            children.append(html.Br())
    return children


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


def get_view_controls(user):
    return [
        action_button(
            button_id=ID_NOTE_EDIT_BUTTON,   
            icon="material-symbols:edit", 
            disabled=True if user is None else False),
    ]

icon_private = DashIconify(
    icon="material-symbols:lock",                    
    width=14, 
    style={"display":"block", "marginLeft":"3px", "color": "#868e96"}
)

icon_public= DashIconify(
    icon="material-symbols:lock-open-right-outline", 
    width=14, 
    style={"display":"block", "marginLeft":"3px", "color": "#868e96"}
)




def note_detail_view(note: Note):
    user = get_user_from_cookies()
    title    = note.title
    controls = [
        action_button(
            button_id={"button":"edit_note", "note_id": note.id},   
            icon="material-symbols:edit", 
            disabled=True if user is None else False
        ),
    ]

    return dmc.Container([
        dmc.Grid([
            dmc.Col(dmc.Title(title),span="content"),
            dmc.Col(dmc.Group(controls, spacing="sm"),
                span="content"
            ),
        ],
            justify="space-between"
        ),
        *note_details(note),
        dmc.ScrollArea(
            children=attachment_area(note.files, False),
            h=150,
            type="hover",
            offsetScrollbars=True
        )
    ])


def note_details(note: Note):
    return [
        dmc.Grid([
            dmc.Col(
                html.Span([
                    dmc.Text(
                        f"{note.author if note.author is not None else 'unknown'} | {pretty_date(note.date) if note.date is not None else '-'} |",
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
                dmc.ScrollArea(
                    children=text_to_html_list(note.description),
                    type="hover",
                    h=150,
                    offsetScrollbars=True
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
    Output(ID_ALERT_DANGER, "is_open", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "children", allow_duplicate=True),
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Input(ID_CONFIRM_DELETE_DIALOG, "submit_n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def deactivate_edit_mode(delete_click, note):
    if delete_click is None or delete_click == 0:
        raise PreventUpdate

    auth_cookie = flask.request.cookies.get("auth")
    response = delete_note(note["data"]["id"], auth_cookie)
    if response == 200:
        return dict(data=None), False, dash.no_update, dash.no_update, dict(entries=[], type="Note")
    else:
        notification = [
            dmc.Title("Something went wrong!", order=6),
            dmc.Text("Could not delete Note."),
            dmc.Text(f"Exited with Status Code: {response} | {responses[response]}", color="dimmed")
        ]
        return dash.no_update, dash.no_update, True, notification, dash.no_update


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Input({"button":"edit_note", "note_id": ALL}, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_TAG_DATA_STORE, "data"),
    prevent_initial_call=True
)
def activate_edit_mode(click, notes, all_tags):
    click_sum = safe_reduce(lambda x, y: x + y, click, 0)
    if ctx.triggered_id is None or click_sum == 0:
        raise PreventUpdate

    for note in notes["entries"]:
       if note["id"] == ctx.triggered_id["note_id"]:
            return dict(data=note), note_form_view(Note(note), all_tags), 650



