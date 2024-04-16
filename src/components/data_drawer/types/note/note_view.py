from http.client import responses

import dash
import dash_mantine_components as dmc
import flask
from pprint import pprint
from dash import html, Output, Input, State, ctx, ALL, ClientsideFunction, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_core_components as dcc

from configuration import API_URL
from src.api.api_note import delete_note
from src.api.api_files import get_file_url
from src.components.media.player import audio_player
from src.components.button.components.action_button import action_button
from src.components.data_drawer.types.note.attachment import attachment_area
from src.components.data_drawer.types.note.form_view import form_content, get_form_controls
from src.config.app_config import CHART_DRAWER_HEIGHT, PRIMARY_COLOR
from src.config.id_config import *
from src.main import app
from src.model.note import Note
from src.model.file import File
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_user_from_cookies
from src.util.util import local_formatted_date, text_to_dash_elements
from src.config.app_config import supported_mime_types

SCROLL_AREA_HEIGHT = 350

def note_view(note: Note, file_height, theme, test_icons = False):
    media_files = []
    documents   = []

    for file in note.files:
        if file.type in supported_mime_types["image"] or file.type in supported_mime_types["audio"]:
            media_files.append(file)
        else:
            documents.append(file)

    media_files = list(sorted(media_files, key=lambda file: file.name.lower()))
    documents   = list(sorted(documents, key=lambda file: file.name.lower()))

    media_files = [f.to_dict() for f in media_files]
    documents   = [f.to_dict() for f in documents]

    return [
            dcc.Store(
                id=ID_NOTE_FILE_STORE, 
                data=dict(media_files=media_files, documents=documents, focus=0, API_URL=API_URL)
                ),
            dmc.Container(
                id=ID_NOTE_CONTAINER,
                children=[
                    *note_detail_view(note, file_height, theme, test_icons)
                    ]
                )
            ]


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


def slideshow(theme, files: list[File]): 
    light_mode = theme["colorScheme"] == "light"
    background = "#F2F2F2" if light_mode else "#373A40"

    file = files[0]

    slideshow_buttons = []
    if len(files) > 1:
        slideshow_buttons = [
                html.Button("❮", id=ID_SLIDESHOW_BTN_LEFT, className="slide-btn slide-btn-left"), 
                html.Button("❯", id=ID_SLIDESHOW_BTN_RIGHT, className="slide-btn slide-btn-right"), 
                ]

    url = get_file_url(file.object_name)
    image_src = ""
    audio_src = ""
    if file.type.startswith("image/"):
        image_src = url
    else:
        audio_src = url

    return [html.Div(
            children=[
                html.Img(id=ID_SLIDESHOW_IMAGE, className="cropped-ofp", src=image_src),
                audio_player(id=ID_AUDIO_PLAYER, light_mode=light_mode, src=audio_src),
        ],
            className="image-box", 
            style={"background": background}
        ),
            *slideshow_buttons
    ]


def note_form_view(note: Note, all_tags):

    is_public = True if note.public == True else False

    return dmc.Container([
        dmc.Grid([
            dmc.Col([
                dmc.Title("Edit / Create Note"),
                dmc.Text(note.author + " • " + local_formatted_date(note.date), color="dimmed", size="sm")
            ],span="content"),
            dmc.Col(dmc.Group(get_form_controls(is_public),spacing="sm", style={"justify-content":"flex-end"}), span="content")
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
            h=435,
            type="hover",
            offsetScrollbars=True
        )
    ])


def note_detail_view(note: Note, file_height, theme, test_icons):
    user        = get_user_from_cookies()
    title       = note.title
    files       = list(sorted(note.files, key=lambda file: file.name.lower()))
    media_files = list(filter(lambda f: f.type.startswith("image/") or f.type.startswith("audio/"), files))

    has_media_files = len(media_files) != 0

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
                dmc.Col(
                    html.Div(
                        id="id-slideshow-container", 
                        className="image-container", 
                        children=slideshow(theme, files) if has_media_files else {}
                        ), className="image-col", span=4),
                    ], justify="space-between", grow=True),
                dmc.Space(h=10),
                *attachment_area(note.files, False),
            ],
            type="hover",
            h=360,
            offsetScrollbars=True)
    ]


@app.callback(
    Output(ID_SLIDESHOW_IMAGE, "src", allow_duplicate=True),
    Output(ID_FOCUSED_MEDIA_STORE, "data", allow_duplicate=True),
    Input(ID_MAP, "clickData"),
    prevent_initial_call=True
)
def map_click(_):
    return "", None

@app.callback(
    Output(ID_CONFIRM_DELETE_DIALOG, "displayed", allow_duplicate=True),
    Input(ID_NOTE_DELETE_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def delete_click(click):
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
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
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
            return dict(data=note), note_form_view(Note(note), all_tags), False, CHART_DRAWER_HEIGHT


# app.clientside_callback(
#     ClientsideFunction(
#         namespace="attachment", function_name="create_blob"
#     ),
#     Output(ID_FOCUSED_MEDIA_STORE, "data"),
#     Output(ID_BLOB_URLS_STORE, "data", allow_duplicate=True),
#     Input({"element": "media", "file_id": ALL}, "n_clicks"),
#     Input(ID_SLIDESHOW_BTN_LEFT, "n_clicks"),
#     Input(ID_SLIDESHOW_BTN_RIGHT, "n_clicks"),
#     State(ID_NOTE_FILE_STORE, "data"),
#     State(ID_BLOB_URLS_STORE, "data"),
#     prevent_initial_call=True
# )


app.clientside_callback(
    ClientsideFunction(
        namespace="attachment", function_name="load_text_blob"
    ),
    Output(ID_NOTE_FILE_STORE, "data"),
    Input({"element": "text", "file_id": ALL}, "n_clicks"),
    State(ID_NOTE_FILE_STORE, "data"),
    prevent_initial_call=True
)


@app.callback(
    Output(ID_NOTE_FILE_STORE, "data", allow_duplicate=True),
    Input({"element": "media", "file_id": ALL}, "n_clicks"),
    State(ID_NOTE_FILE_STORE, "data"),
    prevent_initial_call=True
)
def click_on_attachment(click, data):
    if ctx.triggered_id is None:
        raise PreventUpdate

    files     = data["media_files"]
    documents = data["documents"]
    all_files = [*files, *documents]

    print(click)
    for (idx, file) in enumerate(all_files):
        if ctx.triggered_id["file_id"] == file["id"]:
            data["focus"] = idx

    return data

@app.callback(
    Output(ID_NOTE_FILE_STORE, "data", allow_duplicate=True),
    Input(ID_SLIDESHOW_BTN_RIGHT, "n_clicks"),
    Input(ID_SLIDESHOW_BTN_LEFT, "n_clicks"),
    State(ID_NOTE_FILE_STORE, "data"),
    prevent_initial_call = True
    )
def next_media(_click_r, click_l, data):
    files = data["media_files"]
    idx   = data["focus"]
    if ctx.triggered_id == ID_SLIDESHOW_BTN_RIGHT:
        idx += 1
    else:
        idx -= 1

    idx = idx % len(files)
    data["focus"] = idx
    return data


@app.callback(
    Output(ID_SLIDESHOW_IMAGE, "src"),
    Output(ID_SLIDESHOW_IMAGE, "style"),
    Output(ID_AUDIO, "src"),
    Output(ID_AUDIO_PLAYER, "style"),
    Input(ID_NOTE_FILE_STORE, "data"),
)

def update_focused_image(data):
    if data == None or data == "":
        raise PreventUpdate

    idx = data["focus"]
    if idx < len(data["media_files"]):
        file = data["media_files"][idx]
    else:
        raise PreventUpdate

    visible   = {"display": "flex"}
    invisible = {"display": "none"}

    url = get_file_url(file["object_name"])

    if file["type"].startswith("image"):
        return url, visible, no_update, invisible
    elif file["type"].startswith("audio"):
        return no_update, invisible, url, visible

    raise PreventUpdate


@app.callback(
    Output({"element": "card", "file_id": ALL}, "style"),
    Input(ID_NOTE_FILE_STORE, "data"),
    Input(ID_APP_THEME, 'theme'),
)
def mark_active_card(data, theme):
    default_style = {}
    green_light   = theme["colors"]["mitwelten_green"][6]
    green_dark    = theme["colors"]["mitwelten_green"][8]

    primary_color =  green_light if theme["colorScheme"] == "light" else green_dark
    active_style  = {"border-color": primary_color}

    styles = [default_style] * len(ctx.outputs_list)
    styles[data["focus"]] = active_style

    return styles 


@app.callback(
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_NOTE_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_EDIT_NOTE_STORE, "data"),
    State(ID_CHART_DRAWER, "size"),
    State("id-test-icon-store", "data"),
    prevent_initial_call=True
)
def cancel_click(cancel_click, notes, selected_note, drawer_size, test_icons):

    if ctx.triggered_id == ID_NOTE_FORM_CANCEL_BUTTON:
        if cancel_click is None or cancel_click == 0:
            raise PreventUpdate

    if selected_note["data"] is None:
        raise PreventUpdate

    file_height = 116
    for note in notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            n = Note(note)
            file_height = 116 if len(n.files) > 3 else 50 if len(n.files) > 0 else 0
            drawer_size -= 116 - file_height                    
            if n != Note(selected_note["data"]):
                return True, no_update, no_update, no_update, drawer_size

        return no_update, dict(data=None), note_detail_view(Note(selected_note["data"]), file_height, drawer_size, test_icons), drawer_size 


@app.callback(
    Output("id-slideshow-container", "children"),
    Input(ID_APP_THEME, "theme"),
    State(ID_SLIDESHOW_IMAGE, "src"),
    prevent_initial_call=True
)
def update_player_colors(theme, src):
    return slideshow(theme, src)

