import dash_mantine_components as dmc
import flask

from src.api.api_client import construct_url
from dash import  html, dcc, Output, Input, State, ctx, ALL
from dash.exceptions import PreventUpdate
from src.api.api_files import get_file, get_file_url
from src.components.button.components.action_button import action_button
from src.config.id_config import *
from src.config.app_config import thumbnail_size, supported_mime_types
from src.main import app
from src.model.file import File
from src.util.helper_functions import safe_reduce
from src.api.api_files import get_file, get_file_url


def attachment_area(files: list[File], editable = False):
    auth_cookie = flask.request.cookies.get("auth")

    media_files = []
    documents   = []

    for file in files:
        if file.type in supported_mime_types["image"] or file.type in supported_mime_types["audio"]:
            media_files.append(file)
        else:
            documents.append(file)


    media_files = list(sorted(media_files, key=lambda file: file.name.lower()))
    documents   = list(sorted(documents, key=lambda file: file.name.lower()))

    files = list(sorted(files, key=lambda file: file.name.lower()))
    files = [*media_files, *documents]

    image_cards = [_attachment_card(file, auth_cookie, editable) for file in files]

    return [
        dcc.Download(id=ID_DOWNLOAD),
        dmc.Space(h=10),
        dmc.Stack(image_cards)
    ]


def _attachment_card(file: File, auth_cookie, editable = False): 
    name, ext = file.object_name.split('.')
    thumbnail = f"{name}_{thumbnail_size[0]}x{thumbnail_size[1]}.{ext}"
    is_image = file.type in supported_mime_types["image"]

    element = "text"
    if is_image or file.type in supported_mime_types["audio"]:
        element = "media"

    name_length       = 15 if editable else 25
    is_long_filename  = len(file.name) > name_length
    short_filename    = (file.name[:name_length] + '...') if is_long_filename else file.name

    thumbnail_image = construct_url(f"files/{thumbnail}") if is_image else f"assets/mime/{(file.type).rsplit('/', 1)[1]}.svg"

    return dmc.Card(
            id={"element": "card", "file_id": file.id} if not editable and element == "media" else "",
            children=[
                dmc.CardSection(
                    style={
                        "display": "flex",
                        "overflow": "hidden",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        },
                    children=[
                        dmc.Group(
                            grow=True,
                            children=[
                                dmc.Image(
                                    src=thumbnail_image,
                                    fallbackSrc="https://placehold.co/600x400?text=Placeholder",
                                    w=48,
                                    h=48,
                                    ),
                                dmc.Text(
                                    size="xs",
                                    children=file.name,
                                    )
                                ]),

                        dmc.Group([
                            action_button(
                                button_id={"element": "delete_button", "file_id": file.id},
                                icon="material-symbols:delete",
                                size="sm",
                                variant="transparent"
                                ) if editable else {},

                            action_button(
                                button_id={"element": "download_button", "file_id": file.id}, 
                                icon="material-symbols:download", 
                                size="sm",
                                variant="transparent"
                                ),
                            ], style={"marginRight": "5px"}),
                        ]),
                    ],
            withBorder=True,
            shadow="sm",
            radius="sm",
            )


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
    file = list(filter(lambda f: f["id"] == file_id, files["documents"]))[0]
    if file is None:
        raise PreventUpdate

    object_name = file["object_name"]
    file_type   = file["type"]

    file = get_file(object_name, file_type)

    _, content_string = file.split(',')

    return dict(base64=True, type=file_type, filename=object_name.rsplit('/', 1)[1], content=content_string)

