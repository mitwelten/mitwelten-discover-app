import base64
import json
import uuid

from enum import Enum
from pprint import pprint
import dash_mantine_components as dmc
import flask
from dash import  html, dcc, Output, Input, State, ctx, ALL
from dash.exceptions import PreventUpdate
from src.model.file import File

from src.util.helper_functions import safe_reduce
from src.model.note import Note
from src.api.api_files import add_file, get_file
from src.main import app
from src.config.id_config import *
from src.components.button.components.action_button import action_button


ImageState= Enum('Image_State', ['OK', 'TO_ADD', 'TO_DELETE'])

def attachment_modal(note):
    return dmc.Modal(
            title="Attachments",
            id=ID_ATTACHMENT_EDIT_MODAL,
            zIndex=10000,
            size="lg",
            withCloseButton=True,
            closeOnEscape=True,
            closeOnClickOutside=False,
            children=[attachment_table(note)]
    )



def create_rows(files, image_state: ImageState, is_editable, auth_cookie):
    rows = []
    for file in files:
        rows.append(
            html.Tr(
                children=[
                    html.Td(
                        id={"element": "table", "file_id": file.id, "object_name": file.object_name, "type": file.type},
                        children=dmc.Image(
                            src=get_file(file.object_name, file.type, auth_cookie), # TODO: replace with thumbnail
                        withPlaceholder=True, 
                        width=24)),
                    html.Td(file.name),
                    html.Td(file.type),
                    html.Td(image_state.name),
                    html.Td(dmc.Group([ 
                        (
                            action_button(
                                button_id={"element": "delete_button", "file_id": file.id, "object_name": file.object_name, "type": file.type}, 
                                icon="material-symbols:delete", 
                                size="sm") if is_editable else {}
                        ),
                        (
                            action_button(
                                button_id={"element": "download_button", "file_id": file.id, "object_name": file.object_name, "type": file.type}, 
                                icon="material-symbols:download", 
                                size="sm") if image_state is ImageState.OK else {}
                        ),
                    ])),
                ],
            )
        )
    return rows


def attachment_table(note, attachment_store = None):
    is_editable = note.get("inEditMode", False)
    note = Note(note["data"])

    marked_to_add= attachment_store.get("add", []) if attachment_store is not None else []

    files_ok  = []
    files_del = []
    files_add = [File(file) for file in marked_to_add]
    marked_to_delete = attachment_store.get("delete", []) if attachment_store is not None else []

    for file in note.files:
        if file.id in marked_to_delete:
            files_del.append(file)
        else: 
            files_ok.append(file)

    auth_cookie = flask.request.cookies.get("auth")
    rows_ok     = create_rows(files_ok,  ImageState.OK, is_editable, auth_cookie)
    rows_delete = create_rows(files_del, ImageState.TO_DELETE, is_editable, auth_cookie)
    rows_add    = create_rows(files_add, ImageState.TO_ADD, is_editable, auth_cookie)


    drag_n_dop = dcc.Upload(
        id=ID_IMAGE_UPLOAD,
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

    header = [
        html.Thead(
            html.Tr([
                html.Th(""), # Image
                html.Th("Name"),
                html.Th("Type"),
                html.Th("Status"),
                html.Th(""), # Controls
            ])
        )
    ]

    rows = rows_ok + rows_add + rows_delete
    sorted_rows = list(sorted(rows, key=lambda row: row.children[1].children))

    return dmc.Container([
        drag_n_dop if is_editable else [],

        dmc.Table(
            header + [html.Tbody(children=sorted_rows)],
            striped=True,
            highlightOnHover=True,
            withBorder=False,
            withColumnBorders=False,
        ),

        dmc.Modal(
            id=ID_IMAGE_VIEW_MODAL,
            zIndex=20000,
            size="full",
        ),

        dcc.Download(id="id-download")
    ])


@app.callback(
    Output(ID_IMAGE_VIEW_MODAL, "opened"),
    Output(ID_IMAGE_VIEW_MODAL, "children"),
    Input({"element": "table", "file_id": ALL, "object_name": ALL, "type": ALL}, "n_clicks"),
)
def handle_table_click(_):
    print("handle_table_click")
    if ctx.triggered_id is None:
        raise PreventUpdate
    auth_cookie = flask.request.cookies.get("auth")
    return True, html.Img(src=get_file(ctx.triggered_id["object_name"], ctx.triggered_id["type"], auth_cookie))


@app.callback(
    Output(ID_ATTACHMENT_EDIT_MODAL, "opened", allow_duplicate=True),
    Output(ID_ATTACHMENT_EDIT_MODAL, "children", allow_duplicate=True),
    Input(ID_NOTE_ATTACHMENT_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_NOTE_ATTACHMENT_STORE, "data"),
    prevent_initial_call=True
)
def update_attachment_modal_state(click, notes, selected_note, attachment_store):
    if click == 0 or click is None:
        raise PreventUpdate

    for note in notes["entries"]:
         if note["id"] == selected_note["data"]["id"]:
            return True, attachment_table(selected_note, attachment_store)

    # auth_cookie = flask.request.cookies.get("auth")
    raise PreventUpdate


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
    image = get_file(ctx.triggered_id["object_name"], ctx.triggered_id["type"], auth_cookie)

    content_type, content_string = image.split(',')
    content_type = content_type.split(':')[1].split(';')[0]
    data = dict(base64=True, type=content_type, filename=ctx.triggered_id["object_name"].split('/')[1], content=content_string)
    print("data:")
    pprint(data)
    return data


@app.callback(
    Output(ID_NOTE_ATTACHMENT_STORE, "data", allow_duplicate=True),
    Output(ID_ATTACHMENT_EDIT_MODAL, "children", allow_duplicate=True),
    Input({"element": "delete_button", "file_id": ALL, "object_name": ALL, "type": ALL}, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_NOTE_ATTACHMENT_STORE, "data"),
    prevent_initial_call = True
)
def delete_attachment(click, note, attachments):
    print("delete_attachment")
    click_sum = safe_reduce(lambda x, y: x + y, click, 0)
    if ctx.triggered_id is None or click_sum == 0:
        raise PreventUpdate

    triggered_id = ctx.triggered_id["file_id"]
    added_ids = [a["id"] for a in attachments["add"]]

    # remove attachment from delete list
    if triggered_id in attachments["delete"]:
        attachments["delete"].remove(triggered_id)

        # remove attachment from add list
    elif triggered_id in added_ids:
        attachments["add"] = list( filter(lambda el: el["id"] != triggered_id, attachments["add"]))
        # TODO: remove file from minio

    else:

    # remove attachment from note attachments
    #delete_response = delete_file(ctx.triggered_id["file_id"], auth_cookie)
        files_to_delete = attachments.get("delete", []) # get already to delete marked files
        attachments["delete"] = [*files_to_delete, triggered_id]
    return attachments, attachment_table(note, attachments)


@app.callback(
    Output(ID_NOTE_ATTACHMENT_STORE, "data",  allow_duplicate=True),
    Output(ID_ATTACHMENT_EDIT_MODAL, "children", allow_duplicate=True),
    Input(ID_IMAGE_UPLOAD, "contents"),
    State(ID_IMAGE_UPLOAD, "filename"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State(ID_NOTE_ATTACHMENT_STORE, "data"),
    prevent_initial_call = True
)
def add_attachment(list_of_contents, list_of_names, note, attachments):
    print("add_attachment")
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
        if res.status_code == 200:
            response_content = json.loads(res.content.decode("utf-8"))
            obj_name = response_content["object_name"]
            files_to_add = attachments.get("add", []) # get already to delelte marked files
            uuid_value = uuid.uuid1()
            attachments["add"] = [*files_to_add, {"id": str(uuid_value), "object_name": obj_name, "name": name, "type": content_type}]
            #response = add_file_to_note(note_id, obj_name, name, content_type, auth_cookie)

        uploaded_images.append((name, content))

    return attachments, attachment_table(note, attachments)

