import base64
import json
import pytz

from src.components.notification.notification import notification, NotificationType
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
from src.api.api_files import upload_file,  delete_file
from src.api.api_note import update_note, delete_tag_by_note_id, add_tag_by_note_id, add_file_to_note
from src.config.app_config import supported_mime_types, PRIMARY_COLOR
from src.config.id_config import *
from src.main import app
from src.model.note import Note
from src.util.util import local_formatted_date
from src.components.notification.notification import notification
import logging

logger = logging.getLogger(__name__)



min_width_style = {"minWidth": "200px"}

def header(note: Note): 
    is_public = True if note.public == True else False

    return dmc.Flex(
            justify="space-between",
            children=[
                dmc.Group(
                    children=[
                        dmc.Title("Edit Note", order=4), 
                        dmc.Title(dmc.Text(note.author, c="dimmed", size="sm"), order=4)
                        ]
                    ), 
                dmc.Group(
                    gap="sm", 
                    style={"justifyContent":"flex-end"},
                    children=[
                        dmc.Switch(
                            id=ID_NOTE_EDIT_PUBLIC_FLAG,
                            onLabel=DashIconify(icon="material-symbols:lock", width=15),
                            offLabel=DashIconify(icon="material-symbols:lock-open-right-outline", width=15),
                            size="sm",
                            checked=not is_public
                            ),
                        dmc.ActionIcon(
                            DashIconify(icon="material-symbols:delete", width=20),
                            size="md",
                            variant="transparent",
                            id=ID_NOTE_DELETE_BUTTON,
                            ),
                        ]
                    )
                ], 
            )



def content(note: Note, all_tags, tz):
    accepted_types =",".join(list(chain.from_iterable(supported_mime_types.values())))
    return dmc.Stack(
            gap=5,
            children=[
                dmc.TagsInput(
                    id=ID_NOTE_TAG_SELECT,
                    data=sorted([t["name"] for t in all_tags]) if all_tags else [],
                    value=note.tags,
                    size="xs",
                    mt=5,
                    placeholder="Pick tag from list"),

                dmc.Group(
                    grow=True,
                    children=[
                        dmc.DateInput(
                            id=ID_NOTE_DATE_INPUT, 
                            value=local_formatted_date(note.date, timezone=tz, date_format="%Y-%m-%dT%H:%M:%S"), 
                            valueFormat="DD-MM-YYYY", 
                            size="xs",
                            label="Date"
                            ),
                        dmc.TimeInput(
                            id=ID_NOTE_TIME_INPUT, 
                            value=local_formatted_date(note.date, timezone=tz,date_format="%H:%M:%S"), 
                            withSeconds=True,
                            size="xs",
                            label="Time"
                            ),
                        ]),

                dmc.Group(
                    grow=True,
                    children=[
                        dmc.NumberInput(
                            id=ID_NOTE_EDIT_LAT, 
                            label="Latitude", 
                            value=note.lat, 
                            size="xs", 
                            decimalScale=12),

                        dmc.NumberInput(
                            id=ID_NOTE_EDIT_LON, 
                            label="Longitude", 
                            value=note.lon, 
                            size="xs", 
                            decimalScale=12),
                        ]),

                    dmc.TextInput(
                        id=ID_NOTE_EDIT_TITLE, 
                        value=note.title, 
                        label="Title", 
                        debounce=500, 
                        size="xs",
                        style=min_width_style),


                    dmc.Textarea(
                        id=ID_NOTE_EDIT_DESCRIPTION,
                        value=note.description,
                        label="Description",
                        autosize=True,
                        minRows=7,
                        debounce=500,
                        size="xs",
                        style=min_width_style),

                    dmc.Group(
                            grow=True,
                            children=[
                                dmc.Button(
                                    "Cancel", 
                                    id=ID_NOTE_FORM_CANCEL_BUTTON, 
                                    color="gray"),

                                dmc.Button(
                                    "Save", 
                                    id=ID_NOTE_FORM_SAVE_BUTTON),
                                ]),
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
                        html.Div(
                                id=ID_ATTACHMENTS,
                                children=attachment_area(note.files, True),
                                )
                        ])

def note_form_view(note: Note, all_tags, tz):

    return dmc.Container(
            fluid=True, 
            children=[
                header(note),
                dmc.ScrollArea(
                    h=435,
                    type="hover",
                    offsetScrollbars=True,
                    children=[content(note, all_tags, tz)],
                    )
                ], 
            )


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
    date = datetime.fromisoformat(input_date)
    time = datetime.strptime(input_time, "%H:%M:%S")

    date = date.replace(
            hour=time.hour, 
            minute=time.minute, 
            second=time.second,
            )

    tz = pytz.timezone("UTC")
    utc_date= date.astimezone(tz)

    selected_note["data"]["date"] = utc_date.isoformat()
    return selected_note




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
    Output(ID_NOTIFICATION, "children", allow_duplicate=True),
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
        filename, ext = name.rsplit('.')
        if ext == "jpg":
            ext = "jpeg"
            name = filename + "." + ext 


        # string to split: `data:image/png;base64`
        content_type = content_type.split(':')[1].split(';')[0]

        upload_file_response = upload_file(decoded, name, content_type, auth_cookie)

        if upload_file_response.status_code != 200:
            notify = notification(
                    f"Could not add attachment - {upload_file_response.status_code}", 
                    NotificationType.WENT_WRONG
                    )
            return no_update, no_update, notify

        response_content = json.loads(upload_file_response.content.decode("utf-8"))
        obj_name = response_content["object_name"]
        add_file_to_note_res = add_file_to_note(note_id, obj_name, name, content_type, auth_cookie)

        if add_file_to_note_res.status_code != 200:
            notify = notification(
                    f"Could not add attachment to note- {add_file_to_note_res.status_code}", 
                    NotificationType.WENT_WRONG
                    )
            return no_update, no_update, notify

        new_file_id = json.loads(add_file_to_note_res.content)["file_id"]
        new_files.append(dict(id=new_file_id, object_name=obj_name, name=name, type=content_type))

    note["data"]["file"] = new_files
    new_files = [File(f) for f in new_files]
                
    return dict(data=note["data"]), attachment_area(new_files, True), no_update



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
    Output(ID_NOTIFICATION, "children", allow_duplicate=True),
    Output(ID_TAG_DATA_STORE, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    State(ID_EDIT_NOTE_STORE, "data"),
    State(ID_NOTE_EDIT_TITLE, "value"),
    State(ID_NOTE_EDIT_DESCRIPTION, "value"),
    State(ID_NOTE_EDIT_PUBLIC_FLAG, "checked"),
    State(ID_NOTE_TAG_SELECT, "value"),
    State(ID_NOTE_EDIT_LAT, "value"),
    State(ID_NOTE_EDIT_LON, "value"),
    prevent_initial_call=True
)
def persist_note(click, notes, selected_note, title, description, is_public, tags, lat, lon):
    if selected_note is None or click is None or click == 0:
        raise PreventUpdate
    auth_cookie = flask.request.cookies.get("auth")

    selected_note["data"]["tags"] = [{"name": t} for t in tags]
    note = Note(selected_note["data"])
    note.title = title
    note.description = description
    note.public = not is_public
    note.lat = float(lat)
    note.lon = float(lon)

    original_note = None
    def error_return_values(alert):
        return [
            no_update, 
            no_update, 
            no_update, 
            alert,
            no_update
        ]

    for n in notes["entries"]:
        if n["id"] == note.id:
            original_note = Note(n)

    if original_note is None:
        return error_return_values(notification(f"Note with id {note.id} not found, could not save note!", NotificationType.WENT_WRONG))
 
    res = update_note(note, auth_cookie)
    if res.status_code != 200:
        logger.error(f"Could not save note with id {note.id}!")
        return error_return_values(notification(f"Could not save note with id {note.id}", NotificationType.WENT_WRONG))

    tags_to_delete = find_deleted_tags(note, original_note)
    tags_to_add    = find_added_tags(note, original_note)

    # Persists deleted tag of a note
    if tags_to_delete:
        for t in tags_to_delete:
            del_tag_res = delete_tag_by_note_id(note.id, t, auth_cookie)
            if del_tag_res != 200:
                logger.error(f"Could not delete tag {t} of note with id {note.id}!")
                return error_return_values(notification(f"Could not delete tag {t} of note with id {note.id}!", NotificationType.WENT_WRONG))

    # Persists added tags to a note
    if tags_to_add:
        for t in tags_to_add:
            add_tag_res = add_tag_by_note_id(note.id, t, auth_cookie)
            if add_tag_res != 200:
                logger.error(f"Could not add tag {t} to note with id {note.id}!")
                return error_return_values(notification(f"Could not delete tag {t} of note with id {note.id}!", NotificationType.WENT_WRONG))


    notes["entries"] = [] # refresh note store
    update_tag_store = None if tags_to_add else no_update
    return False, notes, dict(data=None), no_update, update_tag_store 

