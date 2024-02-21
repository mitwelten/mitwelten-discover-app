import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import flask

from dash import  html, dcc, Output, Input, State, ctx, ALL
from dash.exceptions import PreventUpdate
from src.api.api_files import get_file
from src.components.button.components.action_button import action_button
from src.config.id_config import *
from src.main import app
from src.model.file import File
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_user_from_cookies


def attachment_area(files: list[File], editable = False):
    user = get_user_from_cookies()
    if user is None:
        return dmc.Text("Login to see attachments!", color="gray")
    auth_cookie = flask.request.cookies.get("auth")
    files = list(sorted(files, key=lambda file: file.name))

    badges = [attachment_badge(file, auth_cookie, editable) for file in files]

    def get_items():
        idx_counter = 0
        items = []
        for f in files:
            is_image = f.type in ["image/png", "image/jpg", "image/jpeg",  "image/gif"]
            if is_image:
                items.append({
                    "key": {"id": f.id, "object_name": f.object_name, "type": f.type, "index": idx_counter}, 
                    "src": "",
                    "caption": f.name
                })
                idx_counter += 1
    
        return items 

    return [
        dcc.Download(id="id-download"),
        dmc.Modal(
            id="id-image-modal",
            size="lg",
            opened=False, 
            centered=True,
            zIndex=3000000,
            children=dmc.LoadingOverlay(
                id="id-overlay",
                children=html.Div(
                    children=dbc.Carousel(id="id-image-carousel", items=get_items(), className="carousel-fade", variant="dark"),
                    style={"height": "200px", "width": "300px", "display": "flex", "alignItems": "flex-end"},
                ),
                loaderProps={"variant": "dots", "color": "orange", "size": "xl"},
            ),
        ),
        dmc.Space(h=20),
        dmc.SimpleGrid(
            cols=3,
            spacing="lg",
            breakpoints=[
                {"maxWidth": 980 + 400, "cols": 3, "spacing": "lg"},
                {"maxWidth": 800 + 400, "cols": 2, "spacing": "md"},
                {"maxWidth": 700 + 400, "cols": 1, "spacing": "md"},
            ],
            children = badges,
        )
    ]

def attachment_badge(file: File, auth_cookie, editable = False): 
    name, ext = file.object_name.split('.')
    thumbnail = f"{name}_thumbnail.{ext}"
    is_image = file.type in ["image/png", "image/jpg", "image/jpeg",  "image/gif"]

    return html.Div(
        children=[
            html.A(
                href=get_file(file.object_name, file.type, auth_cookie) if not is_image else None,
                target="_blank",
                id={"element": "image" if is_image else "text", "file_id": file.id},
                style={"cursor": "pointer",
                       "display": "flex",
                       "overflow": "hidden",
                       "alignItems": "center",
                       "text-decoration": "none",
                       "color": "black",
                       },
                children=[
                    dmc.Image(
                        src=get_file(thumbnail, file.type, auth_cookie) if is_image else f"assets/mime/{(file.type).rsplit('/', 1)[1]}.svg",
                        withPlaceholder=True, 
                        width=48,
                        height=48,
                    ),
                    dmc.Text(file.name, style={"margin": "0 20px", "min-width": "150px"}), 
                ]),
            action_button(
                button_id={"element": "delete_button", "file_id": file.id},
                icon="material-symbols:delete",
            ) if editable else {},

            action_button(
                button_id={"element": "download_button", "file_id": file.id, "object_name": file.object_name, "type": file.type}, 
                icon="material-symbols:download", 
                size="sm"
            ),
        ], style={'display': 'flex', 'alignItems': 'center', "width": "250px"})



@app.callback(
    Output("id-image-modal", "opened"),
    Input({"element": "image", "file_id": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def open_modal(_):
    return True


@app.callback(
    Output("id-overlay", "children"),
    Input({"element": "image", "file_id": ALL}, "n_clicks"),
    State("id-image-carousel", "items"),
    State("id-image-modal", "opened"),
    prevent_initial_call=True
)
def handle_table_click(click, items, modal_state):
    if modal_state or ctx.triggered_id is None:
        raise PreventUpdate

    auth_cookie = flask.request.cookies.get("auth")

    index = 0
    for i in items:
        # find selected image
        if i["key"]["id"] == ctx.triggered_id["file_id"]:
            index = i["key"]["index"]

        # load image, if it is not already loaded
        if i["src"] == "":
            i["src"] = get_file(i["key"]["object_name"], i["key"]["type"], auth_cookie)

    carousel = dbc.Carousel(id="id-image-carousel", items=items, className="carousel-fade", variant="dark", active_index=index)

    return carousel


@app.callback(
    Output("id-download", "data"),
    Input({"element": "download_button", "file_id": ALL, "object_name": ALL, "type": ALL}, "n_clicks"),
    prevent_initial_call = True
)
def download_attachment(click):
    click_sum = safe_reduce(lambda x, y: x + y, click, 0)
    if ctx.triggered_id is None or click_sum == 0:
        raise PreventUpdate

    auth_cookie = flask.request.cookies.get("auth")
    object_name = ctx.triggered_id["object_name"]
    file_type   = ctx.triggered_id["type"]

    file = get_file(object_name, file_type, auth_cookie)

    _, content_string = file.split(',')

    data = dict(base64=True, type=file_type, filename=object_name.rsplit('/', 1)[1], content=content_string)
    return data

