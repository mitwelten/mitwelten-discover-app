from http.client import responses

import dash
import dash_mantine_components as dmc
import flask
from dash import html, Output, Input, State, ctx, ALL, ClientsideFunction, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from src.api.api_note import delete_note
from src.components.button.components.action_button import action_button
from src.components.data_drawer.types.note.attachment import attachment_area
from src.components.data_drawer.types.note.form_view import form_content, get_form_controls
from src.config.app_config import CHART_DRAWER_HEIGHT, PRIMARY_COLOR
from src.config.id_config import *
from src.main import app
from src.model.note import Note
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_user_from_cookies
from src.util.util import apply_newlines, local_formatted_date


def note_view(note: Note):
    return dmc.Container(
        id=ID_NOTE_CONTAINER,
        children=note_detail_view(note),
        #fluid=True,
        #style={"margin":"0 24px 24px 24px"}
    )


def text_to_html_list(text: str):
    lines = apply_newlines(text)
    return dmc.Spoiler(
        children=lines,
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
        dmc.LoadingOverlay(
            children=html.Img(id=ID_SLIDESHOW_IMAGE, className="cropped-ofp"),
            className="image-box", 
            loaderProps={"variant": "dots"}
        ),
        html.Button( "❮", id=ID_SLIDESHOW_BTN_LEFT, className="slide-btn slide-btn-left"), 
        html.Button( "❯", id=ID_SLIDESHOW_BTN_RIGHT, className="slide-btn slide-btn-right"), 
    ], className="image-container")


def note_form_view(note: Note, all_tags):

    return dmc.Container([
        dmc.Grid([
            dmc.Col([
                dmc.Title("Edit / Create Note"),
                dmc.Text(note.author + " • " + local_formatted_date(note.date), color="dimmed", size="sm")
            ],span="content"),
            dmc.Col(dmc.Group(get_form_controls(note.public),spacing="sm"),
                    span="content"
                    )
        ],
            justify="space-between"
        ),
        *form_content(note, all_tags),
        dmc.ScrollArea(
            id=ID_ATTACHMENTS,
            children=attachment_area(note.files, True),
            h=150,
            type="hover",
            offsetScrollbars=True
        )
    ])


def note_detail_view(note: Note):
    user       = get_user_from_cookies()
    title      = note.title
    files      = list(sorted(note.files, key=lambda file: file.name.lower()))
    images     = list(filter(lambda f: f.type.startswith("image/") , files))
    has_images = len(images) != 0

    media_section = slideshow
    # only_audio_file = list(filter(lambda f: f.type == "audio/mpeg", files))
    # print(only_audio_file)
    # if len(only_audio_file) == len(files):
    #     print("note has only audio files => audio note")
    #     media_section = html.Audio(src="", controls="controls")

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
                dmc.Image(
                    src="assets/markers/note.svg", 
                    alt="note icon", 
                    width="70px", 
                    style={"justifyContent": "flex-end"}), 
                span=1),
        ],
            justify="space-between",
        ),
        dmc.Space(h=10),
        dmc.Divider(size="xs"),
        dmc.Space(h=10),
        dmc.ScrollArea(
            children=[
                dmc.Grid([
                    dmc.Col(text_to_html_list(note.description), span=8),
                    dmc.Col(media_section if user and has_images else {}, className="image-col", span=4),
                ], justify="space-between"),
                dmc.Space(h=10),
                *attachment_area(note.files, False),
            ],
            type="hover",
            h=350,
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

app.clientside_callback(
    ClientsideFunction(
        namespace="attachment", function_name="create_blob"
    ),
    Output(ID_SLIDESHOW_IMAGE, "src"),
    Output(ID_BLOB_URLS_STORE, "data", allow_duplicate=True),
    Input({"element": "image", "file_id": ALL}, "n_clicks"),
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

app.clientside_callback(
    ClientsideFunction(
        namespace="attachment", function_name="load_audio_files"
    ),
    Output({"element": "audio", "file_id": ALL}, "src"),
    Output(ID_BLOB_URLS_STORE, "data", allow_duplicate=True),
    Input({"element": "image", "file_id": ALL}, "n_clicks"),
    State(ID_NOTE_FILE_STORE, "data"),
    State(ID_BLOB_URLS_STORE, "data"),
    prevent_initial_call=True
)

@app.callback(
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_NOTE_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_EDIT_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def cancel_click(cancel_click, notes, selected_note):

    if ctx.triggered_id == ID_NOTE_FORM_CANCEL_BUTTON:
        if cancel_click is None or cancel_click == 0:
            raise PreventUpdate

    if selected_note["data"] is None:
        raise PreventUpdate

    for note in notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            if Note(note) != Note(selected_note["data"]):
                return True, no_update, no_update, no_update

    return no_update, dict(data=None), note_detail_view(Note(selected_note["data"])), CHART_DRAWER_HEIGHT
