import dash_mantine_components as dmc
import flask
from pprint import pprint

from dash import  html, dcc, Output, Input, State, ctx, ALL, MATCH
from dash.exceptions import PreventUpdate
from src.api.api_files import get_file
from src.components.button.components.action_button import action_button
from src.config.id_config import *
from src.config.app_config import thumbnail_size, image_types, audio_types
from src.main import app
from src.model.file import File
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_user_from_cookies

from configuration import API_URL

def attachment_area(files: list[File], editable = False):
    user = get_user_from_cookies()
    if user is None:
        return dmc.Text("Login to see attachments!", color="gray")
    auth_cookie = flask.request.cookies.get("auth")
    files = list(sorted(files, key=lambda file: file.name.lower()))

    image_cards = [_attachment_card(file, auth_cookie, editable) for file in files]

    return [
        dcc.Store(
            id=ID_NOTE_FILE_STORE, 
            data=dict(url=API_URL, files=[f.to_dict() for f in files])
        ),
        dcc.Download(id=ID_DOWNLOAD),
        dmc.Space(h=20),
        dmc.SimpleGrid(
            cols=3,
            spacing="lg",
            breakpoints=[
                {"maxWidth": 980 + 400, "cols": 3, "spacing": "lg"},
                {"maxWidth": 800 + 400, "cols": 2, "spacing": "md"},
                {"maxWidth": 500 + 400, "cols": 1, "spacing": "md"},
            ],
            children = image_cards,
        )
    ]


def _attachment_card(file: File, auth_cookie, editable = False): 
    name, ext = file.object_name.split('.')
    thumbnail = f"{name}_{thumbnail_size[0]}x{thumbnail_size[1]}.{ext}"
    is_image = file.type in image_types

    element = "text"
    if is_image or file.type in audio_types:
        element = "media"

    name_length   = 15 if editable else 25
    long_filename = len(file.name) > name_length
    file_name     = (file.name[:name_length] + '...') if long_filename else file.name

    file_name_component = dmc.Text(file_name, style={"margin": "0 10px"})
    card_title = file_name_component 

    if long_filename:
        card_title = dmc.HoverCard(
            withArrow=True,
            shadow="md",
            children=[
                dmc.HoverCardTarget(file_name_component),
                dmc.HoverCardDropdown(dmc.Text(file.name))
            ]
        )

    return html.Div(
        id={"element": element, "file_id": file.id} if not editable else "",
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "overflow": "hidden",
                    "alignItems": "center",
                    "textDecoration": "none",
                    "color": "black",
                },
                children=[
                    dmc.Image(
                        src=get_file(
                            thumbnail, 
                            file.type, 
                            auth_cookie) if is_image else f"assets/mime/{(file.type).rsplit('/', 1)[1]}.svg",
                        withPlaceholder=True, 
                        width=48,
                        height=48,
                    ),
                    card_title
                ]),
            dmc.Group([
                action_button(
                    button_id={"element": "delete_button", "file_id": file.id},
                    icon="material-symbols:delete",
                    size="sm"
                ) if editable else {},
                
                action_button(
                    button_id={"element": "download_button", "file_id": file.id}, 
                    icon="material-symbols:download", 
                    size="sm"
                ),
            ], ),
        ],
        className="attachment-card",
        style={"cursor":"pointer"} if not editable else {}
    )

@app.callback(
    Output({"element": "media", "file_id": ALL}, "className"),
    Input({"element": "media", "file_id": ALL}, "n_clicks"),
)
def mark_active_card(_click):
    classes = ["attachment-card"] * len(ctx.inputs_list[0])

    if ctx.triggered_id == None:
        classes[0] = f"{classes[0]} attachment-card-active"

    for idx, i in enumerate(ctx.inputs_list[0]):
        if i["id"] == ctx.triggered_id:
            classes[idx] = f"{classes[idx]} attachment-card-active"

    return classes

@app.callback(
    Output(ID_DOWNLOAD, "data"),
    Input({"element": "download_button", "file_id": ALL}, "n_clicks"),
    State(ID_NOTE_FILE_STORE, "data"),
    prevent_initial_call = True
)
def download_attachment(click, files):
    click_sum = safe_reduce(lambda x, y: x + y, click, 0)
    if ctx.triggered_id is None or click_sum == 0:
        raise PreventUpdate

    file_id = ctx.triggered_id["file_id"]
    file = list(filter(lambda f: f["id"] == file_id, files["files"]))[0]
    if file is None:
        raise PreventUpdate
    auth_cookie = flask.request.cookies.get("auth")

    object_name = file["object_name"]
    file_type   = file["type"]

    file = get_file(object_name, file_type, auth_cookie)

    _, content_string = file.split(',')

    return dict(base64=True, type=file_type, filename=object_name.rsplit('/', 1)[1], content=content_string)

