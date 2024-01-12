import dash

import dash_mantine_components as dmc
from dash import Output, Input, ALL, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from src.components.button.components.action_button import action_button
from src.config.id_config import *
from src.main import app
from src.model.note import Note
from src.components.data_drawer.types.note import form_callbacks


def note_form(note: Note, all_tags):
    return dmc.Container([

        dmc.Grid([
            dmc.Col(dmc.Title("Create a new Note"),span="content"),
            dmc.Col(dmc.Group([
                dmc.Switch(
                    id=ID_NOTE_EDIT_PUBLIC_FLAG,
                    offLabel=DashIconify(icon="material-symbols:lock", width=15),
                    onLabel=DashIconify(icon="material-symbols:lock-open-right-outline", width=15),
                    size="sm",
                    checked=note.public
                ),
                action_button(button_id=ID_LOCATION_MODAL_BUTTON, icon="material-symbols:edit-location-alt-outline-sharp"),
                action_button(button_id=ID_ATTACHMENT_MODAL_FORM_BUTTON, icon="material-symbols:attach-file")
            ],
                spacing="sm"
            ),
                span="content"
            )
        ],
            justify="space-between"
        ),

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
                maxRows=9,
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
        dmc.Modal(
            title="Attachments",
            id=ID_ATTACHMENT_FORM_MODAL,
            zIndex=10000,
            children=[
                # html.Div(id="id-image-container"),
                # dmc.Image(src=f"{API_URL}/files/discover/test_img.png"),
                # *[dmc.Text(f"{t.to_dict()}") for t in note.files],
                dmc.Button("Ok", id=ID_SAVE_ATTACHMENT_BUTTON),
            ],
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
    ])


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
    Output(ID_ATTACHMENT_FORM_MODAL, "opened"),
    Output(ID_ALERT_INFO, "is_open"),
    Output(ID_ALERT_INFO, "children"),
    #Output("id-image-container", "children"),
    Input(ID_ATTACHMENT_MODAL_FORM_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def update_attachment_modal_state(click):
    if click == 0 or click is None:
        raise PreventUpdate

    notification = [
        dmc.Title("Sorry, Feature not implemented yet!", order=6),
        dmc.Text("Attachments coming soon...")
    ]
    # auth_cookie = flask.request.cookies.get("auth")
    # file = get_file("test_img.png", auth_cookie)
    return dash.no_update, True, notification


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

    selected_note["data"]["title"]           = title
    selected_note["data"]["description"]     = description
    selected_note["data"]["location"]["lat"] = float(lat)
    selected_note["data"]["location"]["lon"] = float(lon)
    selected_note["data"]["public"]          = is_public
    selected_note["data"]["tags"]            = [{"name": t} for t in tags]

    # if selected note is not modified(dirty), check if note is modified after callback has fired
    is_dirty = True
    found = False
    for note in all_notes["entries"]:
        if note["id"] == selected_note["data"]["id"]:
            found = True
            is_dirty = Note(note) != Note(selected_note["data"])

    if not found:  # note is new created - therefore not in collection
        if title == "" and description == "":
            is_dirty = False  # callback was fired when mounting to de DOM

    is_edited = selected_note.get("inEditMode", False)
    return dict(data=selected_note["data"], inEditMode=is_edited, isDirty=is_dirty), False


@app.callback(
    Output(ID_NOTE_EDIT_LAT, "value", allow_duplicate=True),
    Output(ID_NOTE_EDIT_LON, "value", allow_duplicate=True),
    Input({"role": "Note", "id": ALL, "label": "Node"}, "position"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def change_lat_lon_by_marker_position(_, selected_note):
    """
    Update value of lat & lon text fields when marker is moved and its position changes.
    """
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

    new_position = None
    for pos in dash.ctx.inputs_list[0]:
        if selected_note["data"]["id"] == pos["id"]["id"]:
            new_position = pos["value"]

    return new_position

