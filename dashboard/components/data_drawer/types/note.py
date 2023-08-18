from pprint import pprint

import dash
import dash_mantine_components as dmc
from dash import Output, Input, State, html, dcc, ALL, MATCH
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.components.button.components.action_button import action_button
from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.file import File
from dashboard.model.note import Note
from dashboard.util.user_validation import get_user_from_cookies
from dashboard.util.util import pretty_date
from util.functions import safe_reduce


def list_item(text, icon):
    return dmc.ListItem(
        text,
        icon=dmc.ThemeIcon(
            DashIconify(icon=icon, width=16),
            radius="xl",
            color=PRIMARY_COLOR,
            size=24,
        ),
    )


def create_note_form_container(note: Note):
    user = get_user_from_cookies()
    return dmc.Container([
        dcc.Store({"role": "Notes", "id": note.note_id, "label": "Edit Store"}, data=dict(state=False), storage_type="local"),
        html.Div(
            id={"role": "Notes", "id": note.note_id, "label": "Form"},
            children=note_form_non_editable(note, user),
        ),
        html.Div(
            id={"role": "Notes", "id": note.note_id, "label": "Editable Form"},
            children=note_form_editable(note, user),
            style={"display": "none"}
        )
    ])


@app.callback(
    Output({"role": "Notes", "id": MATCH, "label": "Form"}, "style"),
    Output({"role": "Notes", "id": MATCH, "label": "Editable Form"}, "style"),
    Input({"role": "Notes", "id": MATCH, "label": "Edit Store"}, "data"),
    prevent_initial_call=True
)
def update_form_container(store_data):
    if store_data["state"]:
        return {"display": "none"}, {"display": "block"}
    return {"display": "block"}, {"display": "none"}


def note_form_non_editable(note: Note, user=None):
    return [dmc.Grid([
            dmc.Col(dmc.Title(note.title, order=5), span="content"),
            dmc.Col(dmc.Group([
                action_button({"role": "Notes", "id": note.note_id, "label": "Attachment Button"}, "material-symbols:attach-file"),
                action_button({"role": "Notes", "id": note.note_id, "label": "Edit Button"}, "material-symbols:edit") if user is not None else {}
                ]),
                span="content"
            ),
        ],
            justify="space-between",
        ),
        dmc.Grid([
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(dmc.Divider(size="xs")),
            dmc.Col(
                dmc.Spoiler(
                    dmc.Text(note.description),
                    showLabel="Show more",
                    hideLabel="Hide",
                    maxHeight=50,
                ),
                span=12
            ),
            dmc.Col(dmc.Divider(size="xs")),
            dmc.Col(
                dmc.List(
                    size="md",
                    spacing="sm",
                    children=[
                        list_item(f"Creator: {note.creator}", "material-symbols:person"),
                        list_item(f"Location: {note.lat} / {note.lon}", "material-symbols:location-on-rounded"),
                        list_item(f"Created at: {pretty_date(note.created_at)}", "material-symbols:add-circle"),
                        list_item(f"Updated at: {pretty_date(note.updated_at)}", "material-symbols:edit"),
                    ],
                ),
                span="content"
            )
        ])
    ]


def note_form_editable(note: Note, user):
    return [
        dmc.Grid([
            dmc.Col(dmc.Title(f"Note - {note.node_label}", order=3), span="content"),
            dmc.Col(action_button({"role": "Notes", "id": note.note_id, "label": "Attachment Store"}, "material-symbols:attach-file"), span="content"),
        ],
            justify="space-between",
        ),
        dmc.Grid([
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(dmc.TextInput(id=ID_NOTE_EDIT_TITLE, value=note.title, label="Title", variant="filled"), span=12),
            dmc.Col(dmc.Textarea(id=ID_NOTE_EDIT_DESCRIPTION, value=note.description, label="Description", variant="filled"), span=12),
            dmc.Divider(size="sm"),
            dmc.Col(dmc.TextInput(label="Latitude", value=note.lat, variant="filled"), span=6),
            dmc.Col(dmc.TextInput(label="Longitude", value=note.lon, variant="filled"), span=6),
        ]),
        dmc.Grid([
            dmc.Col(dmc.Button("Cancel", id={"role": "Notes", "id": note.note_id, "label": "Cancel Button"}, type="reset", color="gray"), span="content"),
            dmc.Col(dmc.Button("Save", id={"role": "Notes", "id": note.note_id, "label": "Save Button"}, type="submit"), span="content"),
        ],
            justify="flex-end"
        )
    ]


def create_note_form(notes, note_id, theme):
    for note in notes:
        if note["note_id"] == note_id:
            return create_note_form_container(Note(note))


def attachment_table(note, is_editable=False):
    user = get_user_from_cookies()
    header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Name"),
                    html.Th("Type"),
                    html.Th("Last Modified"),
                    html.Th(""),
                ]
            )
        )
    ]

    rows = []
    for file in note["files"]:
        file = File(file)
        rows.append(
            html.Tr([
                html.Td(file.name),
                html.Td(file.type),
                html.Td(file.last_modified),
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
    html.Div(id='output-image-upload'),
    return dmc.Container(
        dmc.Stack([
            dmc.Table(
                header + body,
                striped=True,
                highlightOnHover=True,
                withBorder=False,
                withColumnBorders=False,
                ),
            drag_n_dop if is_editable else {}
        ]
        )
    )


def parse_contents(content, name, date):
    return dict(content=content, name=name, date=date)


@app.callback(
    Output(ID_NEW_NOTE_STORE, 'data'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'),
    State('upload-image', 'last_modified'),
    State(ID_NEW_NOTE_STORE, 'data')
)
def update_output(list_of_contents, list_of_names, list_of_dates, store):
    if list_of_contents is not None:
        content = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        for c in content:
            store.append(c)
    return store


@app.callback(
    Output('output-image-upload', "children"),
    Input(ID_NEW_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def show_new_notes_from_store(data):
    all_note_titles = []
    for note in data:
        all_note_titles.append(html.Div(note["name"]))
    return all_note_titles


@app.callback(
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input({"role": "Notes", "id": ALL, "label": "Edit Button"}, "n_clicks"),
    prevent_initial_call=True
)
def activate_preventing_marker_clicks(click):
    print("activate prevent marker click: ", click)
    return dict(state=True)


@app.callback(
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input({"role": "Notes", "id": ALL, "label": "Cancel Button"}, "n_clicks"),
    prevent_initial_call=True
)
def activate_preventing_marker_clicks(click):
    print("activate prevent marker click: ", click)
    return dict(state=False)


@app.callback(
    Output({"role": "Notes", "id": MATCH, "label": "Edit Store"}, "data", allow_duplicate=True),
    Input({"role": "Notes", "id": MATCH, "label": "Edit Button"}, "n_clicks"),
    prevent_initial_call=True
)
def update_edit_store_by_click(click):
    if click == 0:
        raise PreventUpdate
    return dict(state=True)


@app.callback(
    Output({"role": "Notes", "id": MATCH, "label": "Edit Store"}, "data", allow_duplicate=True),
    Input({"role": "Notes", "id": MATCH, "label": "Cancel Button"}, "n_clicks"),
    prevent_initial_call=True
)
def update_edit_store_by_click(click):
    if click == 0:
        raise PreventUpdate
    return dict(state=False)


@app.callback(
    Output({"role": "Notes", "id": MATCH, "label": "Node", "lat": ALL, "lon": ALL}, "icon"),
    Output({"role": "Notes", "id": MATCH, "label": "Node", "lat": ALL, "lon": ALL}, "draggable"),
    Input({"role": "Notes", "id": MATCH, "label": "Edit Store"}, "data"),
    prevent_initial_call=True
)
def change_note_icon(store_data):
    if store_data["state"]:
        return [dict(iconUrl="assets/markers/note_move.svg", iconAnchor=[60, 50], iconSize=120)], [True]
    return [dict(iconUrl="assets/markers/note.svg", iconAnchor=[15, 6], iconSize=30)], [False]




# @app.callback(
#     Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
#     Input({"role": "note-edit-button", "id": ALL}, "n_clicks"),
#     State(ID_CURRENT_CHART_DATA_STORE, "data"),
#     State(ID_NOTES_STORE, "data"),
#     prevent_initial_call=True
# )
# def create_editable_note_form(click, chart_data, notes):
#     click_sum = safe_reduce(lambda x, y: x + y, click)
#     if click_sum is None or click_sum == 0:
#         return dash.no_update
#
#     for note in notes:
#         if note["note_id"] == chart_data["id"]:
#             return note_form_editable(Note(note))


# @app.callback(
#     Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
#     Input({"role": "note-cancel-button", "id": ALL}, "n_clicks"),
#     State(ID_CURRENT_CHART_DATA_STORE, "data"),
#     State(ID_NOTES_STORE, "data"),
#     prevent_initial_call=True
# )
# def create_editable_note_form(click, chart_data, notes):
#     click_sum = safe_reduce(lambda x, y: x + y, click)
#     if click_sum is None or click_sum == 0:
#         return dash.no_update
#     for note in notes:
#         if note["note_id"] == chart_data["id"]:
#             return note_form_non_editable(Note(note))


# @app.callback(
#     Output(ID_NOTIFICATION_CONTAINER, "children"),
#     Input({"role": "note-save-button", "id": ALL}, "n_clicks"),
#     prevent_initial_call=True
# )
# def save_edited_note(click):
#     click = safe_reduce(lambda x, y: x + y, click)
#     if click is not None:
#         return create_notification(
#             "Save Note",
#             "Operation under construction",
#             NotificationType.ERROR,
#             "material-symbols:construction"
#         )
#     return dash.no_update


@app.callback(
    # Output(ID_NOTES_LAYER_GROUP, "children"),
    Output(ID_NEW_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
    Input(ID_MAP, "dbl_click_lat_lng"),
    # State(ID_NOTES_LAYER_GROUP, "children"),
    prevent_initial_call=True
)
def handle_double_click(click):
    user = get_user_from_cookies()
    if user is None:
        notification = create_notification(
            "Operation not permitted",
            "Log in to create notes!",
            NotificationType.WARN
        )
        return dash.no_update, notification

    # marker = dl.Marker(
    #     position=[click[0], click[1]],
    #     icon=dict(iconUrl="assets/markers/note.svg", iconAnchor=[15, 6], iconSize=30),
    # )
    # if markers is None:
    #     markers = []
    # return [*markers, marker], dict(lat=click[0], lon=click[1]), dash.no_update,
    return dict(lat=click[0], lon=click[1]), dash.no_update
