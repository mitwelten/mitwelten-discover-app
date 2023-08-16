from datetime import datetime
from pprint import pprint

import dash
import dash_mantine_components as dmc
from dash import Output, Input, ALL, State
import dash
import dash_leaflet as dl
from dash import Output, Input, State, html, dcc

import dash_mantine_components as dmc

from configuration import PRIMARY_COLOR
from dashboard.components.button.components.action_button import action_button
from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.file import File
from dashboard.util.user_validation import get_user_from_cookies

from dashboard.api.api_client import get_fake_note_by_id
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.model.note import Note


def note_form_editable(note: Note):
    return dmc.Container([
        dcc.Store("id-current-note-store", data=note.to_dict()),
        dcc.Store("id-new-note-store", data=[]),
        dmc.Grid([
            dmc.Col(dmc.Title(f"Note - {note.node_label}", order=3), span="content"),
            dmc.Col(action_button("id-note-attachment-button", "material-symbols:attach-file"), span="content"),
        ],
            justify="space-between",
        ),
        dmc.Grid([
            dmc.Col(dmc.ChipGroup([dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in note.tags]), span=12),
            dmc.Col(dmc.TextInput(value=note.title, label="Title", variant="filled"), span=12),
            dmc.Col(dmc.Textarea(value=note.description, label="Description", variant="filled"), span=12),
            dmc.Divider(size="sm"),
            dmc.Col(dmc.TextInput(label="Latitude", value=note.lat, variant="filled"), span=6),
            dmc.Col(dmc.TextInput(label="Longitude", value=note.lon, variant="filled"), span=6),
        ]),
        dmc.Grid([
            dmc.Col(dmc.Button("Cancel", type="reset", color="gray"), span="content"),
            dmc.Col(dmc.Button("Save", type="submit"), span="content"),
        ],
            justify="flex-end"
        )
    ],
    )


def create_note_form(notes, note_id, theme):
    print(notes)
    for note in notes:
        if note["note_id"] == note_id:
            print(Note(note).to_dict())
            return note_form_editable(Note(note))


def create_form(note):
    return dmc.Text(f"Form of: {note}")


def attachment_table(note):
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
                    action_button("id-attachment-delete-button", "material-symbols:delete", size="sm"),
                    action_button("id-attachment-download-button", "material-symbols:download", size="sm")
                ])),
            ])
        )

    body = [html.Tbody(rows)]
    return dmc.Container(
        dmc.Stack([
            dmc.Table(
                header + body,
                striped=True,
                highlightOnHover=True,
                withBorder=False,
                withColumnBorders=False,
                ),
            dcc.Upload(
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
            ),
            html.Div(id='output-image-upload'),
        ]
        )
    )


def parse_contents(content, name, date):
    return dict(content=content, name=name, date=date)


@app.callback(
    Output("id-new-note-store", 'data'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'),
    State('upload-image', 'last_modified'),
    State("id-new-note-store", 'data')
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
    Output("id-note-attachment-modal", "opened"),
    Output("id-note-attachment-modal", "children"),
    Input("id-note-attachment-button", "n_clicks"),
    State("id-current-note-store", "data"),
    prevent_initial_call=True
)
def open_attachment_modal(click, data):
    return click != 0, attachment_table(data)


@app.callback(
    Output('output-image-upload', "children"),
    Input("id-new-note-store", "data"),
    prevent_initial_call=True
)
def show_new_notes_from_store(data):
    all_note_titles = []
    for note in data:
        all_note_titles.append(html.Div(note["name"]))
    return all_note_titles

