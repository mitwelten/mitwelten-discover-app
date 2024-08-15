import dash_mantine_components as dmc
from dash import html, Output, Input, State, ctx, ALL, ClientsideFunction, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_core_components as dcc

from src.components.notification.notification import NotificationType, notification
from configuration import API_URL
from src.components.data_drawer.header import bottom_drawer_content
from src.api.api_files import get_file_url
from src.components.data_drawer.types.note.form_view import note_form_view
from src.config.app_config import CHART_DRAWER_HEIGHT, PRIMARY_COLOR
from src.config.id_config import *
from src.main import app
from src.model.note import Note
from src.model.file import File
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_user_from_cookies
from src.util.util import get_drawer_size_by_number_of_files, text_to_html_list
from src.config.app_config import supported_mime_types
from src.components.data_drawer.types.note.confirm import confirm_dialogs
from src.api.api_files import get_file_url

def note_view(note: Note, theme, tz, edit=False, all_tags=None):
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
        children = note_form_view(note, all_tags, tz)
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


icon_private = DashIconify(
    icon="material-symbols:lock",                    
    width=14, 
    style={"display":"block", "marginLeft":"3px", "color": "#868e96"}
)

def audio_card(file):
    return dmc.Card(
            withBorder=True,
            shadow="sm",
            radius="md",
            h="80%",
            w="80%",
            children=[
                dmc.CardSection(
                    dmc.Center(
                        h=120,
                        style={"height": "80px"},
                        children=DashIconify(icon="wpf:audio-wave", width=100),
                        ),
                    ),
                dmc.Center(
                    children=dmc.Text(
                        file.name, 
                        fw=500, 
                        m=20, 
                        style={"textOverflow": "ellipsis", "overflow": "hidden"}
                        ), 
                    style={"textOverflow": "ellipsis"}),
                html.Audio(
                    src=get_file_url(file.object_name), 
                    controls=True, 
                    style={"width": "100%"}
                    )
                ],
            )


def doc_card(file):
    return dmc.Card(
            withBorder=True,
            shadow="sm",
            radius="md",
            h="80%",
            w="80%",
            children=[
                html.Div(
                    id={"element": "text", "file_id": file.id},
                    className="docu-card",
                    style={
                        "cursor": "pointer", 
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center"
                        },
                    children=[
                        dmc.Stack(
                            children=[
                                dmc.Image(
                                    style={"height": "80px"},
                                    p=20,
                                    src=f"assets/mime/{(file.type).rsplit('/', 1)[1]}.svg",
                                    ),
                                dmc.Text(file.name, fw=500, m=20),
                                ]),
                            ]),
                    ],
            )


def carousel_card(file: File):
    if file.type.startswith("image/"):
        return dmc.Image(src=get_file_url(file.object_name))
    elif file.type.startswith("audio/"):
        return audio_card(file)
    else :
        return doc_card(file)


def note_detail_view(note: Note, theme):
    user            = get_user_from_cookies()
    files           = list(sorted(note.files, key=lambda file: file.name.lower()))
    has_media_files = len(files) != 0
    private         = icon_private if not note.public else None
    edit_button     = dmc.ActionIcon(
            DashIconify(icon="material-symbols:edit", width=20),
            size="md",
            radius="xl",
            variant="light",
            id={"button":"edit_note", "note_id": note.id},
            )

    carousel = dmc.Carousel(
            orientation="horizontal",
            align="center",
            slideGap={ "base": "sm" },
            height="300",
            loop=True,
            controlsOffset="md",
            withIndicators=True,
            bg=PRIMARY_COLOR,
            children=[
                dmc.CarouselSlide(
                    display="flex",
                    style={"justifyContent": "center", "alignItems": "center"},
                    children=carousel_card(img)) for img in files],
            )

    side_by_side = dmc.SimpleGrid(
            cols={"base": 1, "sm": 2},
            spacing={"base": 10, "sm": "xl"},
            verticalSpacing={"base": "md"},
            children = [text_to_html_list(note.description), carousel],
        )

    content = side_by_side if has_media_files else text_to_html_list(note.description)

    return [
            bottom_drawer_content(
                note.title,
                note.tags,
                "docu.svg",
                theme,
                dmc.Group([private, edit_button]),
                note.author
                ),
            dmc.Container(content, fluid=True, pt=20),
            ]


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
    State(ID_TIMEZONE_STORE, "data"),
    prevent_initial_call=True
)
def activate_edit_mode(click, notes, all_tags, tz):

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
            if n.author == user.full_name or "internal" in user.roles:
                return dict(data=note), note_form_view(n, all_tags["all"], tz["tz"]), False, CHART_DRAWER_HEIGHT, no_update
            else:
                n = notification("Only the author can edit this note!", NotificationType.NOT_PERMITTED)
                return no_update, no_update, no_update, no_update, n 


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
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "size", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_EDIT_NOTE_STORE, "data"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_APP_THEME, "forceColorScheme"),
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
            return no_update, dict(data=None), note_view(Note(note), theme, False), drawer_size, False
    raise PreventUpdate


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
    State(ID_APP_THEME, "forceColorScheme"),
    State(ID_TIMEZONE_STORE, "data"),
    prevent_initial_call=True,
)
def deactivate_edit_mode(cancel_click, selected_note, notes, drawer_size, theme, tz):
    if cancel_click is None or cancel_click == 0:
        raise PreventUpdate
    
    for note in notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            n = Note(note)
            drawer_size = get_drawer_size_by_number_of_files(len(n.files))
            return dict(data=None), drawer_size, True, note_view(n, theme, tz["tz"]), True

    raise PreventUpdate


