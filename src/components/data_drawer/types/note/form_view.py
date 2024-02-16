from hashlib import new
from types import new_class
import dash

import base64
import json
import flask
from datetime import datetime
from pprint import pprint
import dash_mantine_components as dmc
from dash import Output, Input, ALL, State, dcc, ctx, html, MATCH, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from src.model.file import File
from http.client import responses
from src.components.button.components.action_button import action_button
from src.components.data_drawer.types.note.attachment import attachment_area
from src.util.helper_functions import safe_reduce
from src.api.api_files import add_file, add_file_to_note, delete_file
from src.api.api_files import add_file_to_note, delete_file
from src.api.api_note import create_note, update_note, delete_tag_by_note_id, add_tag_by_note_id
from configuration import PRIMARY_COLOR
from src.config.id_config import *
from src.main import app
from src.model.note import Note



def get_form_controls(public:bool = False):
    return [
        dmc.Switch(
            id=ID_NOTE_EDIT_PUBLIC_FLAG,
            offLabel=DashIconify(icon="material-symbols:lock", width=15),
            onLabel=DashIconify(icon="material-symbols:lock-open-right-outline", width=15),
            size="sm",
            checked=public
        ),
        action_button(
            button_id=ID_NOTE_DELETE_BUTTON,   
            icon="material-symbols:delete", 
        ),
        action_button(
            button_id=ID_LOCATION_MODAL_BUTTON, 
            icon="material-symbols:edit-location-alt-outline-sharp"
        ),
    ]


def note_form_view(note: Note, all_tags):
    controls = get_form_controls(note.public)

    return dmc.Container([
        dmc.Grid([
            dmc.Col(dmc.Title("Edit / Create Note"),span="content"),
            dmc.Col(dmc.Group(controls, spacing="sm"),
                span="content"
            ),
        ],
            justify="space-between"
        ),
        *from_content(note, all_tags),
        dmc.ScrollArea(
            id=ID_ATTACHMENTS,
            children=attachment_area(note.files, True),
            h=150,
            type="hover",
            offsetScrollbars=True
        )
    ])

def from_content(note: Note, all_tags):
    return [
        dmc.Grid([
            # title and description section
            dmc.Col(dmc.MultiSelect(
                id=ID_NOTE_TAG_SELECT,
                label="Select Tags",
                data=[t["name"] for t in all_tags],
                value=note.tags,
                searchable=True,
                nothingFound="No Tags found",
                size="sm",
            ),
                span="auto"
            ),
            dmc.Col(dmc.TextInput(
                id=ID_NEW_TAG_INPUT,
                label="Create new Tag",
                size="sm",
                rightSection=dmc.ActionIcon(
                    DashIconify(icon="material-symbols:add-circle", width=20),
                    size="lg",
                    variant="subtle",
                    id=ID_CREATE_NEW_TAG_BUTTON,
                    n_clicks=0,
                    color=PRIMARY_COLOR
                )
            ),
                span="auto"
            ),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_TITLE, value=note.title, label="Title", debounce=500), span=12),
            dmc.Col(dmc.Textarea(
                id=ID_NOTE_EDIT_DESCRIPTION,
                value=note.description,
                label="Description",
                autosize=True,
                minRows=4,
                maxRows=4,
                debounce=500
            ),
                    span=12),
        ]),
        dmc.Grid([
            dmc.Col([dmc.Button("Cancel", id=ID_NOTE_FORM_CANCEL_BUTTON, type="reset",   color="gray")], span="content"),
            dmc.Col(dmc.Button("Save",    id=ID_NOTE_FORM_SAVE_BUTTON,   type="submit"), span="content"),
        ],
            justify="flex-end"
        ),

        dmc.Space(h=10),

        dcc.Upload(
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
            },
            multiple=True
        ),

        dmc.Modal(
            title="Edit Location",
            id=ID_EDIT_LOCATION_MODAL,
            zIndex=10000,
            children=[
                dmc.Grid([
                    dmc.Col(dmc.NumberInput(id=ID_NOTE_EDIT_LAT, label="Latitude",  value=note.lat, size="sm", precision=12), span=6),
                    dmc.Col(dmc.NumberInput(id=ID_NOTE_EDIT_LON, label="Longitude", value=note.lon, size="sm", precision=12), span=6),
                    dmc.Col(dmc.Button("Save", id=ID_SAVE_LOCATION_BUTTON, type="submit"), span=12)
                ]),
            ],
        )
    ]


@app.callback(
    Output(ID_NOTE_TAG_SELECT, "data"),
    Output(ID_NOTE_TAG_SELECT, "value"),
    Input(ID_CREATE_NEW_TAG_BUTTON, "n_clicks"),
    State(ID_NEW_TAG_INPUT, "value"),
    State(ID_NOTE_TAG_SELECT, "data"),
    State(ID_NOTE_TAG_SELECT, "value"),
)
def update_selected_tags(_, text_input, existing_tags, actual_selected):
    if text_input is None or text_input == "":
        raise PreventUpdate
    return [*existing_tags, text_input], [*actual_selected, text_input]


@app.callback(
    Output(ID_EDIT_LOCATION_MODAL, "opened"),
    Input(ID_LOCATION_MODAL_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def update_location_modal_state(click):
    if click == 0 or click is None:
        raise PreventUpdate
    return True


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_EDIT_LOCATION_MODAL, "opened", allow_duplicate=True),
    Input(ID_NOTE_EDIT_TITLE, "value"),
    Input(ID_NOTE_EDIT_DESCRIPTION, "value"),
    Input(ID_NOTE_EDIT_PUBLIC_FLAG, "checked"),
    Input(ID_SAVE_LOCATION_BUTTON, "n_clicks"),
    Input(ID_NOTE_TAG_SELECT, "value"),
    Input(ID_NOTE_EDIT_LAT, "value"),
    Input(ID_NOTE_EDIT_LON, "value"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    prevent_initial_call=True
)
def update_note_store_by_form(title, description, is_public, location_click, tags, lat, lon, selected_note, all_notes):
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate
    print("updaste selected note data")

    # TODO: use switch case
    selected_note["data"]["title"]           = title
    selected_note["data"]["description"]     = description
    selected_note["data"]["location"]["lat"] = float(lat)
    selected_note["data"]["location"]["lon"] = float(lon)
    selected_note["data"]["public"]          = is_public
    selected_note["data"]["tags"]            = [{"name": t} for t in tags]

    return selected_note, False # TODO: False here used to close location modal dialog, solve in another way


@app.callback(
    Output(ID_NOTE_EDIT_LAT, "value", allow_duplicate=True),
    Output(ID_NOTE_EDIT_LON, "value", allow_duplicate=True),
    Input({"role": "Note", "id": ALL, "label": "Node"}, "latlng"),
    prevent_initial_call=True
)
def marker_click(coordinates):
    if coordinates is None or len(coordinates) == 0:
        raise PreventUpdate

    assert len(coordinates) > 0
    latlng = list(filter( lambda x: x is not None, coordinates))
    if len(latlng) == 0:
        raise PreventUpdate

    return float(latlng[0]["lat"]), float(latlng[0]["lng"])


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data",  allow_duplicate=True),
    Output(ID_ATTACHMENTS, "children", allow_duplicate=True),
    Input(ID_IMAGE_UPLOAD, "contents"),
    State(ID_IMAGE_UPLOAD, "filename"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call = True
)
def add_attachment(list_of_contents, list_of_names, note):
    print("add_attachment")
    if list_of_contents is None:
        raise PreventUpdate

    auth_cookie = flask.request.cookies.get("auth")
    note_id = note["data"]["id"]
    files = note["data"]["files"]
    new_files = files

    for content, name in zip(list_of_contents, list_of_names):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        # string to split: `data:image/png;base64`
        content_type = content_type.split(':')[1].split(';')[0]

        res = add_file(decoded, name, content_type, auth_cookie)

        # TODO: handle error case
        if res.status_code == 200:
            response_content = json.loads(res.content.decode("utf-8"))
            obj_name = response_content["object_name"]
            response = add_file_to_note(note_id, obj_name, name, content_type, auth_cookie)

            if response.status_code == 200:

                new_file_id = json.loads(response.content)["file_id"]
                new_files.append(dict(id=new_file_id, object_name=obj_name, name=name, type=content_type))

    note["data"]["file"] = new_files
    new_files = [File(f) for f in new_files]
                
    return dict(data=note["data"]), attachment_area(new_files, True)


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data",  allow_duplicate=True),
    Output(ID_ATTACHMENTS, "children", allow_duplicate=True),
    Input({"element": "delete_button", "file_id": ALL}, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call = True
)
def delete_attachment(click, note):
    click_sum = safe_reduce(lambda x, y: x + y, click, 0)
    if ctx.triggered_id is None or click_sum == 0:
        raise PreventUpdate

    triggered_id = ctx.triggered_id["file_id"]

    auth_cookie = flask.request.cookies.get("auth")
    res = delete_file(triggered_id, auth_cookie)
    if res.status_code == 200:

        new_files = []
        files = note["data"]["files"]
        for file in files:
            if file["id"] != triggered_id:
                new_files.append(file)

        note["data"]["files"] = new_files
        new_files = [File(f) for f in new_files]
        return dict(data=note["data"]), attachment_area(new_files, True)

    raise PreventUpdate


def find_new_tags(note_dict, all_tags):
    note_tags = note_dict["data"]["tags"]
    result_list = []
    for item in note_tags:
        if item not in all_tags:
            result_list.append(item["name"])

    return result_list

def find_deleted_tags(modified_note, original_note):
    result = []
    for t in original_note.tags:
        if t not in modified_note.tags:
            result.append(t)
    return result


def find_added_tags(modified_note, original_note):
    result = []
    for t in modified_note.tags:
        if t not in original_note.tags:
            result.append(t)
    return result


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "children", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "is_open", allow_duplicate=True),
    Output(ID_TAG_DATA_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def persist_note(click, notes, selected_note):
    if selected_note is None or click is None or click == 0:
        raise PreventUpdate
    auth_cookie = flask.request.cookies.get("auth")
    modified_note = Note(selected_note["data"])
    modified_note.date = datetime.now().isoformat()

    tags_to_delete  = []
    tags_to_add     = []

    found = False
    response_code = 400 # TODO: find another way to handle this
    returned_note_id = None

    for note in notes["entries"]:
        if note["id"] == modified_note.id:
            #  Note already exists
            found = True
            note = Note(note)
            tags_to_delete = find_deleted_tags(modified_note, note)
            tags_to_add = find_added_tags(modified_note, note)
            res = update_note(modified_note, auth_cookie)
            response_code = res.status_code
            returned_note_id = res.json().get("note_id", -1)

    if not found:
        # new created note
        res = create_note(modified_note, auth_cookie)
        response_code = res.status_code
        returned_note_id = res.json().get("note_id", -1)
        tags_to_add = modified_note.tags

    if response_code != 200 or returned_note_id == -1:
        notification = [
            dmc.Title("Something went wrong!", order=6),
            dmc.Text("Could not save Note."),
            dmc.Text(f"Exited with Status Code: {response_code} | {responses[response_code]}", color="dimmed")]
        return no_update, no_update, no_update, dict(add=[], delete=[]), True, notification

    # TODO: handle error
    # Persists deleted tag of a note
    if tags_to_delete:
        for t in tags_to_delete:
            delete_tag_by_note_id(returned_note_id, t, auth_cookie)
    # Persists added tags to a note
    if tags_to_add:
        for t in tags_to_add:
            add_tag_by_note_id(returned_note_id, t, auth_cookie)


    notes["entries"] = [] # refresh note store
    update_tag_store = None if tags_to_add else no_update
    return False, notes, dict(data=None), no_update, no_update, update_tag_store 


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def cancel_click(cancel_click, notes, selected_note):

    print("map_click callback")
    if ctx.triggered_id == ID_NOTE_FORM_CANCEL_BUTTON:
        if cancel_click is None or cancel_click == 0:
            raise PreventUpdate

    print("map_click")

    if selected_note["data"] is None:
        return False, dash.no_update, dash.no_update

    for note in notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            if Note(note) != Note(selected_note["data"]):
                return dash.no_update, True, dash.no_update

    return False, dash.no_update, dict(data=None)


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_CHART_DRAWER, "opened"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def map_click(drawer_state, notes, selected_note):

    if ctx.triggered_id == ID_CHART_DRAWER:
        if drawer_state:
            raise PreventUpdate #  drawer state is opening - no action required

    if selected_note["data"] is None:
        return False, dash.no_update, dash.no_update

    for note in notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            if Note(note) != Note(selected_note["data"]):
                return dash.no_update, True, dash.no_update

    return False, dash.no_update, dict(data=None)
