import dash
import dash_mantine_components as dmc
from dash import Output, Input, State, html, dcc
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


def note_form_non_editable(note: Note):
    user = get_user_from_cookies()
    return dmc.Container([
        dcc.Store("id-is-editable-store", data=dict(state=False)),
        dmc.Grid([
            dmc.Col(dmc.Title(note.title, order=5), span="content"),
            dmc.Col(dmc.Group([
                action_button(ID_NOTE_OPEN_MODAL_BUTTON, "material-symbols:attach-file"),
                action_button(ID_NOTE_EDIT_BUTTON, "material-symbols:edit") if user is not None else {}
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
        ]),
    ],
    )


def note_form_editable(note: Note):
    return dmc.Container([
        dcc.Store("id-is-editable-store", data=dict(state=True)),
        dmc.Grid([
            dmc.Col(dmc.Title(f"Note - {note.node_label}", order=3), span="content"),
            dmc.Col(action_button(ID_NOTE_OPEN_MODAL_BUTTON, "material-symbols:attach-file"), span="content"),
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
            dmc.Col(dmc.Button("Cancel", id=ID_NOTE_CANCEL_EDIT_BUTTON, type="reset", color="gray"), span="content"),
            dmc.Col(dmc.Button("Save", id=ID_NOTE_SAVE_EDIT_BUTTON, type="submit"), span="content"),
        ],
            justify="flex-end"
        )
    ],
    )


def create_note_form(notes, note_id, theme):
    for note in notes:
        if note["note_id"] == note_id:
            return note_form_non_editable(Note(note))


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
    Output(ID_NOTE_ATTACHMENT_MODAL, "opened"),
    Output(ID_NOTE_ATTACHMENT_MODAL, "children"),
    Input(ID_NOTE_OPEN_MODAL_BUTTON, "n_clicks"),
    State(ID_CURRENT_CHART_DATA_STORE, "data"),
    State(ID_NOTES_STORE, "data"),
    State("id-is-editable-store", "data"),
    prevent_initial_call=True
)
def open_attachment_modal(click, chart_data, notes, is_editable):
    if click != 0:
        for note in notes:
            if note["note_id"] == chart_data["id"]:
                return True, attachment_table(note, is_editable["state"])
    return dash.no_update, dash.no_update


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
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Input(ID_NOTE_EDIT_BUTTON, "n_clicks"),
    State(ID_CURRENT_CHART_DATA_STORE, "data"),
    State(ID_NOTES_STORE, "data"),
    prevent_initial_call=True
)
def create_editable_note_form(click, chart_data, notes):
    if click == 0:
        return dash.no_update
    for note in notes:
        if note["note_id"] == chart_data["id"]:
            return note_form_editable(Note(note))


@app.callback(
    Output(ID_CHART_CONTAINER, "children", allow_duplicate=True),
    Input(ID_NOTE_CANCEL_EDIT_BUTTON, "n_clicks"),
    State(ID_CURRENT_CHART_DATA_STORE, "data"),
    State(ID_NOTES_STORE, "data"),
    prevent_initial_call=True
)
def create_editable_note_form(click, chart_data, notes):
    if click is None:
        return dash.no_update
    for note in notes:
        if note["note_id"] == chart_data["id"]:
            return note_form_non_editable(Note(note))


@app.callback(
    Output(ID_NOTIFICATION_CONTAINER, "children"),
    Input(ID_NOTE_SAVE_EDIT_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def save_edited_note(click):
    print(click)
    if click is not None:
        return create_notification(
            "Save Note",
            "Operation under construction",
            NotificationType.ERROR,
            "material-symbols:construction"
        )
    return dash.no_update
