import base64
import json
import flask
from datetime import datetime
import dash_mantine_components as dmc
from itertools import chain
from dash import Output, Input, ALL, State, dcc, ctx, html, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from src.model.file import File
from src.components.button.components.action_button import action_button
from src.components.data_drawer.types.note.attachment import attachment_area
from src.util.helper_functions import safe_reduce
from src.api.api_files import add_file,  delete_file
from src.api.api_note import update_note, delete_tag_by_note_id, add_tag_by_note_id, add_file_to_note
from src.config.app_config import supported_mime_types, PRIMARY_COLOR
from src.config.id_config import *
from src.main import app
from src.model.note import Note
from src.util.util import local_formatted_date
from src.error.notifications import notification, response_notification

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

min_width_style = {"minWidth": "200px"}

def form_content(note: Note, all_tags):

    accepted_types =",".join( list(chain.from_iterable(supported_mime_types.values())))
    return [
        dmc.Grid([
            # title and description section
            dmc.Col(dmc.MultiSelect(
                id=ID_NOTE_TAG_SELECT,
                label="Select Tags",
                data=sorted([t["name"] for t in all_tags]),
                value=note.tags,
                searchable=True,
                nothingFound="No Tags found",
                size="sm",
            ),
                span=6,
                style=min_width_style
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
                    color=PRIMARY_COLOR,
                )
            ),
                span=6,
                style=min_width_style,
            ),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_TITLE, value=note.title, label="Title", debounce=500, style=min_width_style), span=6),
            dmc.Col(dmc.DatePicker(id=ID_NOTE_DATE_INPUT, value=local_formatted_date(note.date, "%Y-%m-%dT%H:%M:%S"), label="Date", style={"minWidth": "200px"}), span=4),
            dmc.Col(dmc.TimeInput(id=ID_NOTE_TIME_INPUT, value=local_formatted_date(note.date, "%Y-%m-%dT%H:%M:%S"), label="Time", style={"minWidth": "50"}), span=2),
            dmc.Col(dmc.Textarea(
                id=ID_NOTE_EDIT_DESCRIPTION,
                value=note.description,
                label="Description",
                autosize=True,
                minRows=4,
                maxRows=4,
                debounce=500,
                style=min_width_style
            ),
                    span=12),
        ],grow=True),
        dmc.Grid([
            dmc.Col([dmc.Button("Cancel", id=ID_NOTE_FORM_CANCEL_BUTTON, type="reset",   color="gray")], span="content"),
            dmc.Col(dmc.Button("Save",    id=ID_NOTE_FORM_SAVE_BUTTON,   type="submit"), span="content"),
        ],
            justify="flex-end"
        ),

        dmc.Space(h=10),

        dcc.Upload(
            id=ID_IMAGE_UPLOAD,
            children=[
                "Drag and Drop or ", 
                html.A("Select files", style={"fontWeight": "bold"})
            ] ,
            accept=accepted_types,
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'cursor': 'pointer',
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
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_DATE_INPUT, "value"),
    Input(ID_NOTE_TIME_INPUT, "value"),
    State(ID_EDIT_NOTE_STORE, "data"),
    prevent_initial_call = True
)
def update_date_time(input_date, input_time, selected_note):
    if selected_note["data"] is None:
        raise PreventUpdate
    time = datetime.fromisoformat(input_time)
    date = datetime.fromisoformat(input_date)
    date = date.replace(hour=time.hour, minute=time.minute, second=time.second, tzinfo=time.tzinfo)

    selected_note["data"]["date"] = date.isoformat()
    return selected_note


@app.callback(
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_EDIT_LOCATION_MODAL, "opened", allow_duplicate=True),
    Input(ID_NOTE_EDIT_TITLE, "value"),
    Input(ID_NOTE_EDIT_DESCRIPTION, "value"),
    Input(ID_NOTE_EDIT_PUBLIC_FLAG, "checked"),
    Input(ID_SAVE_LOCATION_BUTTON, "n_clicks"),
    Input(ID_NOTE_TAG_SELECT, "value"),
    Input(ID_NOTE_EDIT_LAT, "value"),
    Input(ID_NOTE_EDIT_LON, "value"),
    State(ID_EDIT_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def update_note_store_by_form(title, description, is_public, location_click, tags, lat, lon, selected_note):
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

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
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_ATTACHMENTS, "children", allow_duplicate=True),
    Input(ID_IMAGE_UPLOAD, "contents"),
    State(ID_IMAGE_UPLOAD, "filename"),
    State(ID_EDIT_NOTE_STORE, "data"),
    prevent_initial_call = True
)
def add_attachment(list_of_contents, list_of_names, note):
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
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_ATTACHMENTS, "children", allow_duplicate=True),
    Input({"element": "delete_button", "file_id": ALL}, "n_clicks"),
    State(ID_EDIT_NOTE_STORE, "data"),
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
    Output(ID_EDIT_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "is_open", allow_duplicate=True),
    Output(ID_ALERT_DANGER, "children", allow_duplicate=True),
    Output(ID_TAG_DATA_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_EDIT_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def persist_note(click, notes, selected_note):
    if selected_note is None or click is None or click == 0:
        raise PreventUpdate
    auth_cookie = flask.request.cookies.get("auth")

    note = Note(selected_note["data"])

    original_note = None
    def error_return_values(alert):
        return [
            no_update, 
            no_update, 
            no_update, 
            True, 
            alert,
            no_update
        ]

    for n in notes["entries"]:
        if n["id"] == note.id:
            original_note = Note(n)

    if original_note is None:
        return error_return_values(notification(f"Note with id {note.id} not found, could not save note!"))
 
    res = update_note(note, auth_cookie)
    if res.status_code != 200:
        return error_return_values(response_notification(res.status_code, f"Could not save note with id {note.id}"))

    tags_to_delete = find_deleted_tags(note, original_note)
    tags_to_add    = find_added_tags(note, original_note)

    # Persists deleted tag of a note
    if tags_to_delete:
        for t in tags_to_delete:
            del_tag_res = delete_tag_by_note_id(note.id, t, auth_cookie)
            if del_tag_res != 200:
                return error_return_values(response_notification(del_tag_res, f"Could not delete tag {t} of note with id {note.id}!"))

    # Persists added tags to a note
    if tags_to_add:
        for t in tags_to_add:
            add_tag_res = add_tag_by_note_id(note.id, t, auth_cookie)
            if add_tag_res != 200:
                return error_return_values(response_notification(add_tag_res, f"Could not delete tag {t} of note with id {note.id}!"))


    notes["entries"] = [] # refresh note store
    update_tag_store = None if tags_to_add else no_update
    return False, notes, dict(data=None), no_update, no_update, update_tag_store 

