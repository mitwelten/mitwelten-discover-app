import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import flask
from configuration import API_URL
from pprint import pprint

from dash import  html, dcc, Output, Input, State, ctx, ALL, MATCH, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
from src.api.api_files import get_file
from src.components.button.components.action_button import action_button
from src.config.id_config import *
from src.config.app_config import thumbnail_size
from src.main import app
from src.model.file import File
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_user_from_cookies


def attachment_area(files: list[File], editable = False):
    user = get_user_from_cookies()
    if user is None:
        return dmc.Text("Login to see attachments!", color="gray")
    auth_cookie = flask.request.cookies.get("auth")
    files = list(sorted(files, key=lambda file: file.name.lower()))

    image_cards = [attachment_card(file, auth_cookie, editable) for file in files]

    return [
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

def attachment_card(file: File, auth_cookie, editable = False): 
    name, ext = file.object_name.split('.')
    thumbnail = f"{name}_{thumbnail_size[0]}x{thumbnail_size[1]}.{ext}"
    is_image = file.type in ["image/png", "image/jpg", "image/jpeg",  "image/gif"]

    return html.Div(
        children=[
            html.Div(
                id={"element": "image" if is_image else "text", "file_id": file.id},
                style={"cursor": "pointer",
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
                    dmc.Text(file.name, style={"margin": "0 20px"}), 
                ]),
            html.Div([
                action_button(
                    button_id={"element": "delete_button", "file_id": file.id},
                    icon="material-symbols:delete",
                ) if editable else {},
                
                action_button(
                    button_id={"element": "download_button", "file_id": file.id}, 
                    icon="material-symbols:download", 
                    size="sm"
                ),
            ], style={"marginRight": "10px", "display": "flex", "alignItems": "center"}),
        ],
        className="attachment-card"
    )

    #clientside_callback(
    #    ClientsideFunction(
    #        namespace="attachment", function_name="create_blob"
    #    ),
    #    Output(ID_BLOB_URLS_STORE, "data", allow_duplicate=True),
    #    Input({"element": "text", "file_id": ALL}, "n_clicks"),
    #    State(ID_NOTE_FILE_STORE, "data"),
    #    prevent_initial_call = True
    #)

clientside_callback(
    ClientsideFunction(
        namespace="attachment", function_name="clear_blob"
    ),
    Output(ID_BLOB_URLS_STORE, "data", allow_duplicate=True),
    Input(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_BLOB_URLS_STORE, "data"),
    prevent_initial_call = True
)

clientside_callback(
    ClientsideFunction(
        namespace="attachment", function_name="create_blob"
    ),
    Output("id-image", "src"),
    Output(ID_BLOB_URLS_STORE, "data"),
    Input({"element": "image", "file_id": ALL}, "n_clicks"),
    Input("img-btn-left", "n_clicks"),
    Input("img-btn-right", "n_clicks"),
    State(ID_NOTE_FILE_STORE, "data"),
    State(ID_BLOB_URLS_STORE, "data"),
    prevent_initial_call=True
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
    file = list(filter(lambda f: f["id"] == file_id, files["files"]))[0]
    if file is None:
        raise PreventUpdate
    auth_cookie = flask.request.cookies.get("auth")

    object_name = file["object_name"]
    file_type   = file["type"]

    file = get_file(object_name, file_type, auth_cookie)

    _, content_string = file.split(',')

    return dict(base64=True, type=file_type, filename=object_name.rsplit('/', 1)[1], content=content_string)

