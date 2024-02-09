import base64
import datetime
import json

import dash_mantine_components as dmc
import flask
from dash import html, dcc, dash, Output, Input, State, ctx, no_update, dash_table
from dash.exceptions import PreventUpdate

from src.model.note import Note
from src.api.api_files import add_file, add_file_to_note
from src.main import app
from src.config.id_config import *
from src.components.button.components.action_button import action_button
from src.util.user_validation import get_user_from_cookies

def attachment_modal(note, editable=False):
    return dmc.Modal(
            title="Attachments",
            id=ID_ATTACHMENT_EDIT_MODAL,
            zIndex=10000,
            children=[attachment_table(note, editable)]
    )


def attachment_table(note: Note, is_editable=False):
    user = get_user_from_cookies()
    header = [
        html.Thead(
            html.Tr([
                html.Th("Name"),
                html.Th("Type"),
                html.Th("Last Modified"),
                html.Th(""),
            ])
        )
    ]

    rows = []
    for file in note.files:
        rows.append(
            html.Tr([
                html.Td(file.name),
                html.Td(file.type),
                html.Td(file.object_name),
                html.Td(dmc.Group([
                    (action_button("id-attachment-delete-button", "material-symbols:delete", size="sm")
                     if user is not None and is_editable else {}),
                    action_button("id-attachment-download-button", "material-symbols:download", size="sm")
                ])),
            ])
        )

    body = [html.Tbody(rows)]
    drag_n_dop = dcc.Upload(
        id='upload-image',
        children="Click or Drag and Drop",
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    )
    return dmc.Container([
        dmc.Table(
            header + body,
            striped=True,
            highlightOnHover=True,
            withBorder=False,
            withColumnBorders=False,
            ),
        drag_n_dop if is_editable else {},
        html.Div(id="output-image-upload")
    ])


@app.callback(
    Output(ID_ATTACHMENT_EDIT_MODAL, "opened"),
    Output(ID_ATTACHMENT_EDIT_MODAL, "children"),
    Input(ID_NOTE_ATTACHMENT_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def update_attachment_modal_state(click, notes, selected_note):
    if click == 0 or click is None:
        raise PreventUpdate

    for note in notes["entries"]:
         if note["id"] == selected_note["data"]["id"]:
            return True, [attachment_table(Note(note), selected_note["inEditMode"])]

    # auth_cookie = flask.request.cookies.get("auth")
    raise PreventUpdate


def create_list_item(image: tuple[str, str]):
    return dmc.ListItem([
        dmc.Image(src = image[1], width=50),
        dmc.Text(image[0]),
    ])


def create_list_components_from(images: list[tuple[str,str]]):
    item = [create_list_item(image) for image in images]
    image_list = dmc.List (item)
    #html.Img(src=contents),
    return image_list 


@app.callback(
    Output("output-image-upload", "children"),
    Input("upload-image", "contents"),
    State("upload-image", "filename"),
    State(ID_SELECTED_NOTE_STORE, "data")
)
def update_output(list_of_contents, list_of_names, note):
    if list_of_contents is None:
        raise PreventUpdate
    auth_cookie = flask.request.cookies.get("auth")

    uploaded_images : list[tuple[str, str]]= []
    for content, name in zip(list_of_contents, list_of_names):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        # string to split: `data:image/png;base64`
        content_type = content_type.split(':')[1].split(';')[0]

        res = add_file(decoded, name, auth_cookie)

        # TODO: handle error case
        print("1. status code: ", res.status_code)
        print("1. return value: ", res.content)
        if res.status_code == 200:
            id = note["data"]["id"]
            response_content = json.loads(res.content.decode("utf-8"))
            obj_name = response_content["object_name"]
            response = add_file_to_note(id, obj_name, name, content_type, auth_cookie)
            print("2. status code: ",  response.status_code)
            print("2. return value: ", response.content)

        uploaded_images.append((name, content))

    return create_list_components_from(uploaded_images)


@app.callback(
    Output(ID_NOTE_REFRESH_STORE, "data"),
    Input(ID_ATTACHMENT_EDIT_MODAL, "opened"),
    State(ID_NOTE_REFRESH_STORE, "data"),
    prevent_initial_call = True
)
def update_note_store(modal_state, refresh_store):
    if modal_state is False:
        return dict(state=(not refresh_store["state"]))
    raise PreventUpdate
