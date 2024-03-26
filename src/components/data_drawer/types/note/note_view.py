from http.client import responses
import re

import dash
import dash_mantine_components as dmc
import flask
from dash import html, Output, Input, State, ctx, ALL, ClientsideFunction, no_update, dcc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from urllib.parse import urlparse

from src.api.api_note import delete_note
from src.components.media.player import audio_player
from src.components.button.components.action_button import action_button
from src.components.data_drawer.types.note.attachment import attachment_area
from src.components.data_drawer.types.note.form_view import form_content, get_form_controls
from src.config.app_config import CHART_DRAWER_HEIGHT, PRIMARY_COLOR
from src.config.id_config import *
from src.main import app
from src.model.note import Note
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_user_from_cookies
from src.util.util import local_formatted_date, text_to_dash_elements


def note_view(note: Note, test_icons = False):
    return dmc.Container(
        id=ID_NOTE_CONTAINER,
        children=[
            *note_detail_view(note, test_icons)
        ]
    )


def text_to_html_list(text: str):
    elems = text_to_dash_elements(text)
    return dmc.Spoiler(
        children=elems,
        showLabel="Show more",
        hideLabel="Hide",
        maxHeight=150
    )


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


slideshow = html.Div([
        html.Div(
            children=[
                html.Img(id=ID_SLIDESHOW_IMAGE, className="cropped-ofp"),
                audio_player(id=ID_AUDIO_PLAYER),
        ],
            className="image-box", 
        ),
        html.Button("❮", id=ID_SLIDESHOW_BTN_LEFT, className="slide-btn slide-btn-left"), 
        html.Button("❯", id=ID_SLIDESHOW_BTN_RIGHT, className="slide-btn slide-btn-right"), 
    ], className="image-container")


def note_form_view(note: Note, all_tags):

    return dmc.Container([
        dmc.Grid([
            dmc.Col([
                dmc.Title("Edit / Create Note"),
                dmc.Text(note.author + " • " + local_formatted_date(note.date), color="dimmed", size="sm")
            ],span="content"),
            dmc.Col(dmc.Group(get_form_controls(note.public),spacing="sm", style={"justify-content":"flex-end"}), span="content")
        ],
            justify="space-between",
            grow=True
        ),
        dmc.ScrollArea(
            children=[
                *form_content(note, all_tags),
                html.Div(
                    id=ID_ATTACHMENTS,
                    children=attachment_area(note.files, True),
                )
            ],
            h=550,
            type="hover",
            offsetScrollbars=True
        )
    ])


def note_detail_view(note: Note, test_icons):
    user       = get_user_from_cookies()
    title      = note.title
    files      = list(sorted(note.files, key=lambda file: file.name.lower()))
    images     = list(filter(lambda f: f.type.startswith("image/") or f.type.startswith("audio/"), files))
    has_images = len(images) != 0
    return [dmc.Grid([
            dmc.Col(
                dmc.Stack([
                    dmc.Group([
                        dmc.Title(title),
                        action_button(
                            button_id={"button":"edit_note", "note_id": note.id},
                            icon="material-symbols:edit", 
                            disabled=True if user is None else False
                        ),
                    ]),
                    dmc.Grid(
                        children=[
                        dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span="content"),
                        dmc.Col(dmc.Text(f"{note.author} | {local_formatted_date(note.date)}", align="end", color="dimmed", size="sm"), span="content"),
                    ],
                        justify="space-between",
                        grow=True
                    ),
                ]), span=11),
            dmc.Col(

            dmc.MediaQuery(
                dmc.Image(
                    src="assets/markers/test/info_comment.svg" if test_icons else "assets/markers/note.svg",
                    alt="note icon", 
                    style={"justifyContent": "flex-end", "width": "50px"}), 
                smallerThan=1015,
                styles={"display":"none"}
            ),
            style={"min-width":"50px"},
                span="content"),
        ], justify="space-between", grow=True),
    
        dmc.Space(h=10),
        dmc.Divider(size="xs"),
        dmc.Space(h=10),
        dmc.ScrollArea(
            children=[
                dmc.Grid([
                    dmc.Col(text_to_html_list(note.description), span=8),
                    dmc.Col(slideshow if user and has_images else {}, className="image-col", span=4),
                ], justify="space-between", grow=True),
                dmc.Space(h=10),
                *attachment_area(note.files, False),
            ],
            type="hover",
            h=360,
            offsetScrollbars=True)
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
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "is_open", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "children", allow_duplicate=True),
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Input(ID_CONFIRM_DELETE_DIALOG, "submit_n_clicks"),
    State(ID_EDIT_NOTE_STORE, "data"),
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
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_NOTE_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
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
            return dict(data=note), note_form_view(Note(note), all_tags), 650, False


app.clientside_callback(
    ClientsideFunction(
        namespace="attachment", function_name="create_blob"
    ),
    Output(ID_FOCUSED_MEDIA_STORE, "data"),
    Output(ID_BLOB_URLS_STORE, "data", allow_duplicate=True),
    Input({"element": "media", "file_id": ALL}, "n_clicks"),
    Input(ID_SLIDESHOW_BTN_LEFT, "n_clicks"),
    Input(ID_SLIDESHOW_BTN_RIGHT, "n_clicks"),
    State(ID_NOTE_FILE_STORE, "data"),
    State(ID_BLOB_URLS_STORE, "data"),
    prevent_initial_call=True
)


app.clientside_callback(
    ClientsideFunction(
        namespace="attachment", function_name="load_text_blob"
    ),
    Output(ID_BLOB_URLS_STORE, "data", allow_duplicate=True),
    Input({"element": "text", "file_id": ALL}, "n_clicks"),
    State(ID_NOTE_FILE_STORE, "data"),
    State(ID_BLOB_URLS_STORE, "data"),
    prevent_initial_call=True
)


@app.callback(
    Output(ID_SLIDESHOW_IMAGE, "src"),
    Output(ID_SLIDESHOW_IMAGE, "style"),
    Output(ID_AUDIO, "src"),
    Output(ID_AUDIO_PLAYER, "style"),
    Input(ID_FOCUSED_MEDIA_STORE, "data"),
)
def update_focused_image(data):
    visible   = {"display": "flex"}
    invisible = {"display": "none"}

    if data["type"].startswith("image"):
        return data["url"], visible, no_update, invisible
    elif data["type"].startswith("audio"):
        return no_update, invisible, data["url"], visible

    raise PreventUpdate


@app.callback(
    Output({"element": "media", "file_id": ALL}, "className"),
    Input(ID_FOCUSED_MEDIA_STORE, "data"),
)
def mark_active_card(data):
    classes = ["attachment-card"] * len(ctx.outputs_list)

    if ctx.triggered_id == None:
        classes[0] = f"{classes[0]} attachment-card-active"

    for idx, i in enumerate(ctx.outputs_list):
        if i["id"]["file_id"] == data["id"]:
            classes[idx] = f"{classes[idx]} attachment-card-active"

    return classes

@app.callback(
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_NOTE_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_EDIT_NOTE_STORE, "data"),
    State("id-test-icon-store", "data"),
    prevent_initial_call=True
)
def cancel_click(cancel_click, notes, selected_note, test_icons):

    if ctx.triggered_id == ID_NOTE_FORM_CANCEL_BUTTON:
        if cancel_click is None or cancel_click == 0:
            raise PreventUpdate

    if selected_note["data"] is None:
        raise PreventUpdate

    for note in notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            if Note(note) != Note(selected_note["data"]):
                return True, no_update, no_update, no_update

    return no_update, dict(data=None), note_detail_view(Note(selected_note["data"]), test_icons), CHART_DRAWER_HEIGHT
