import dash_mantine_components as dmc
from dash import html, Output, Input, State, ctx, ALL, ClientsideFunction, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_core_components as dcc
from pprint import pprint

from src.components.notification.notification import NotificationType, notification
from configuration import API_URL
from src.components.data_drawer.header import bottom_drawer_content
from src.components.media.slideshow import slideshow
from src.api.api_files import get_file_url
from src.components.button.components.action_button import action_button
from src.components.data_drawer.types.note.attachment import attachment_area
from src.components.data_drawer.types.note.form_view import form_content, get_form_controls
from src.config.app_config import CHART_DRAWER_HEIGHT
from src.config.id_config import *
from src.main import app
from src.model.note import Note
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_user_from_cookies
from src.util.util import local_formatted_date, text_to_dash_elements, get_drawer_size_by_number_of_files
from src.config.app_config import supported_mime_types
from src.components.data_drawer.types.note.confirm import confirm_dialogs


def note_view(note: Note, theme, edit=False, all_tags=None):
    media_files = []
    documents   = []

    for file in note.files:
        if file.type in supported_mime_types["image"] or file.type in supported_mime_types["audio"]:
            media_files.append(file)
        else:
            documents.append(file)

    media_files = list(sorted(media_files, key=lambda file: file.name.lower()))
    documents   = list(sorted(documents,   key=lambda file: file.name.lower()))

    media_files = [f.to_dict() for f in media_files]
    documents   = [f.to_dict() for f in documents]


    if edit:
        children = note_form_view(note, all_tags)
    else:
        children = note_detail_view(note, theme)

    return [
            dcc.Store(
                id=ID_NOTE_FILE_STORE, 
                data=dict(media_files=media_files, documents=documents, focus=0, API_URL=API_URL)
                ),
            html.Div(
                id=ID_NOTE_CONTAINER,
                children=children,
                style={"maxWidth": "1200px"}
                ),
            *confirm_dialogs
            ]


def text_to_html_list(text: str):
    elems = text_to_dash_elements(text)
    return dmc.Spoiler(
        children=elems,
        showLabel="Show more",
        hideLabel="Hide",
        maxHeight=150
    )


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


def note_form_view(note: Note, all_tags):
    is_public = True if note.public == True else False

    return dmc.Container([
        dmc.Group([
            dmc.Title("Edit Note"),
            dmc.Group(get_form_controls(is_public),spacing="sm", style={"justifyContent":"flex-end"})
            ], position="apart"),
        dmc.Text(note.author + " • " + local_formatted_date(note.date), color="dimmed", size="sm"),
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
        ], fluid=True, style={"marginTop": "20px"})


def note_detail_view(note: Note, theme):
    user            = get_user_from_cookies()
    files           = list(sorted(note.files, key=lambda file: file.name.lower()))
    media_files     = list(filter(lambda f: f.type.startswith("image/") or f.type.startswith("audio/"), files))
    has_media_files = len(media_files) != 0
    private         = icon_private if not note.public else None
    edit_button     = action_button(button_id={"button":"edit_note", "note_id": note.id},
                                icon="material-symbols:edit", 
                                disabled=True if user is None else False)

    content = dmc.Container(
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
                offsetScrollbars=True,
                style={"marginTop": "10px"}
                ),
            fluid=True,
            )
    return [
            bottom_drawer_content(
                note.title,
                note.tags,
                "docu.svg",
                theme,
                dmc.Group([private, edit_button]),
                note.author
                ),
            content
            ]


@app.callback(
    Output(ID_SLIDESHOW_IMAGE, "src", allow_duplicate=True),
    Input(ID_MAP, "clickData"),
    prevent_initial_call=True
)
def map_click(_):
    return ""

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
    Output(ID_NOTE_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Output(ID_NOTIFICATION, "children", allow_duplicate=True),
    Input({"button":"edit_note", "note_id": ALL}, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_TAG_DATA_STORE, "data"),
    prevent_initial_call=True
)
def activate_edit_mode(click, notes, all_tags):

    click_sum = safe_reduce(lambda x, y: x + y, click, 0)
    if ctx.triggered_id is None or click_sum == 0:
        raise PreventUpdate

    user = get_user_from_cookies()
    if user is None:
        n = notification("Log in to edit notes!", NotificationType.NOT_PERMITTED)
        return no_update, no_update, no_update, no_update, n

    for note in notes["entries"]:
        if note["id"] == ctx.triggered_id["note_id"]:
            n = Note(note)
            if n.author != user.full_name:
                n = notification("Only the author can edit this note!", NotificationType.NOT_PERMITTED)
                return no_update, no_update, no_update, no_update, n 

            return dict(data=note), note_form_view(n, all_tags["all"]), False, CHART_DRAWER_HEIGHT, no_update


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
    State({"element": "card", "file_id": ALL}, "style"),
)
def mark_active_card(data, theme, cards):
    default_style = {}
    green_light   = theme["colors"]["mitwelten_green"][6]
    green_dark    = theme["colors"]["mitwelten_green"][8]

    primary_color =  green_light if theme["colorScheme"] == "light" else green_dark
    active_style  = {"borderColor": primary_color}

    styles = [default_style] * len(ctx.outputs_list)
    styles[data["focus"]] = active_style

    return styles 



@app.callback(
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_EDIT_NOTE_STORE, "data"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True
)
def cancel_click(cancel_click, notes, selected_note, drawer_size, theme):
    if cancel_click is None or cancel_click == 0:
        raise PreventUpdate

    if selected_note["data"] is None:
        raise PreventUpdate

    for note in notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            n = Note(note)
            if n != Note(selected_note["data"]):
                return True, no_update, no_update, no_update, False

            drawer_size = get_drawer_size_by_number_of_files(len(n.files))
            return no_update, dict(data=None), note_view(Note(note), 0, theme), drawer_size, True
    raise PreventUpdate


@app.callback(
    Output("id-slideshow-container", "children"),
    Input(ID_APP_THEME, "theme"),
    State(ID_SLIDESHOW_IMAGE, "src"),
    prevent_initial_call=True
)
def update_player_colors(theme, src):
    return slideshow(theme, src)


@app.callback(
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_NOTE_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Input(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "submit_n_clicks"),
    State(ID_EDIT_NOTE_STORE, "data"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_APP_THEME, "theme"),
    prevent_initial_call=True,
)
def deactivate_edit_mode(cancel_click, selected_note, notes, drawer_size, theme):
    if cancel_click is None or cancel_click == 0:
        raise PreventUpdate
    
    for note in notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            n = Note(note)
            drawer_size = get_drawer_size_by_number_of_files(len(n.files))
            return dict(data=None), drawer_size, True, note_view(n, theme), True

    raise PreventUpdate
