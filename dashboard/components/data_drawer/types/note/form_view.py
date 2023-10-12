import dash

import dash_mantine_components as dmc
from dash import Output, Input, ALL, State, html
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.components.button.components.action_button import action_button
from dashboard.config.id_config import *
from dashboard.maindash import app
from dashboard.model.note import Note

wrapper_style = dict(
    position="relative",
    transition="None",
    transform="None",
    left=0,
    top=0,
    width="100%",
    borderRadius="4px"
)


def note_form(note: Note, all_tags):

    return [
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
                action_button(button_id="id-location-modal-button", icon="material-symbols:edit-location-alt-outline-sharp"),
                action_button(button_id="id-attachment-modal-button", icon="material-symbols:attach-file")
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
                id="id_note_tag_select",
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
                id="id-new-tag-input",
                label="Create new Tag",
                size="sm",
                rightSection=dmc.ActionIcon(
                    DashIconify(icon="material-symbols:add-circle", width=20),
                    size="lg",
                    variant="subtle",
                    id="id-create-new-tag-button",
                    n_clicks=0,
                    color=PRIMARY_COLOR
                )
            ),
                span="auto"
            ),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_TITLE, value=note.title, label="Title"), span=12),
            dmc.Col(dmc.Textarea(id=ID_NOTE_EDIT_DESCRIPTION, value=note.description, label="Description", autosize=True, maxRows=9), span=12),
        ]),
        dmc.Grid([
            dmc.Col([dmc.Button("Cancel", id=ID_NOTE_FORM_CANCEL_BUTTON, type="reset", color="gray")], span="content"),
            dmc.Col(dmc.Button("Save", id=ID_NOTE_FORM_SAVE_BUTTON, type="submit"), span="content"),
        ],
            justify="flex-end"
        ),
        dmc.Modal(
            title="Select Tags",
            id="ID_NOTE_CHIPS_MODAL",
            zIndex=10000,
            children=[
                dmc.Space(h=20),
                dmc.Center(dmc.Button("Ok", id="ID_NOTE_CLOSE_CHIP_MODAL_BUTTON")),
            ],
        ),
        dmc.Modal(
            title="Edit Location",
            id="id_edit_location_modal",
            zIndex=10000,
            children=[
                dmc.Grid([
                    dmc.Col(dmc.NumberInput(id=ID_NOTE_EDIT_LAT, label="Latitude",  value=note.lat, size="sm", precision=12), span=6),
                    dmc.Col(dmc.NumberInput(id=ID_NOTE_EDIT_LON, label="Longitude", value=note.lon, size="sm", precision=12), span=6),
                    dmc.Col(dmc.Button("Save", id="id-save-location-button", type="submit"), span=12)
                ]),
            ],
        ),
    ]

@app.callback(
    Output("id_note_tag_select", "data"),
    Output("id_note_tag_select", "value"),
    Input("id-create-new-tag-button", "n_clicks"),
    State("id-new-tag-input", "value"),
    State("id_note_tag_select", "data"),
    State("id_note_tag_select", "value"),
)
def update_selected_tags(_, text_input, existing_tags, actual_selected):
    if text_input is None or text_input == "":
        raise PreventUpdate
    return [*existing_tags, text_input], [*actual_selected, text_input]


@app.callback(
    Output("id_edit_location_modal", "opened"),
    Input("id-location-modal-button", "n_clicks"),
    State("id_edit_location_modal", "opened"),
    prevent_initial_call=True
)
def update_location_modal_state(click, state):
    if click == 0 or click is None:
        raise PreventUpdate
    return True


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output("id_edit_location_modal", "opened", allow_duplicate=True),
    Input(ID_NOTE_EDIT_TITLE, "value"),
    Input(ID_NOTE_EDIT_DESCRIPTION, "value"),
    Input(ID_NOTE_EDIT_PUBLIC_FLAG, "checked"),
    Input("id-save-location-button", "n_clicks"),
    State(ID_NOTE_EDIT_LAT, "value"),
    State(ID_NOTE_EDIT_LON, "value"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    State({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    prevent_initial_call=True
)
def update_note_store_by_form(title, description, is_public, location_click, lat, lon, selected_note, all_notes):
    if location_click == 0 or location_click is None:
        raise PreventUpdate
    if selected_note is None or selected_note["data"] is None:
        raise PreventUpdate

    selected_note["data"]["title"] = title
    selected_note["data"]["description"] = description
    selected_note["data"]["location"]["lat"] = float(lat)
    selected_note["data"]["location"]["lon"] = float(lon)
    selected_note["data"]["public"] = is_public

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

