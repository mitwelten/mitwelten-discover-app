import dash
import dash_leaflet as dl
from dash import Output, Input, State, html, dcc

import dash_mantine_components as dmc
from dashboard.components.button.components.action_button import action_button
from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.util.user_validation import get_user_from_cookies


def modal_content(data):
    return dmc.Stack([
        dmc.TextInput(label="Title", required=True, variant="filled"),
        dmc.Textarea(label="Description", variant="filled"),
        dmc.Divider(size="sm"),
        dmc.Text("Location"),
        dmc.Group([
            dmc.TextInput(label="Latitude", value=data["lat"], required=True, variant="filled"),
            dmc.TextInput(label="Longitude", value=data["lon"], required=True, variant="filled"),
        ],
            grow=True
        ),
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
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
            # Allow multiple files to be uploaded
            multiple=True
        ),
        dmc.Button("Create", type="submit"),
    ])


def note_modal():
    return dmc.Modal(
        title="New Note",
        id=ID_NOTE_MODAL,
        zIndex=100000,
        size="lg",
        children=[
            dmc.Text("Note")
        ]
    )

@app.callback(
    Output(ID_NOTE_MODAL, "opened"),
    Output(ID_NOTE_MODAL, "children"),
    Input(ID_NEW_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def open_note_modal(data):
    return True, modal_content(data)




@app.callback(
    # Output(ID_NOTES_LAYER_GROUP, "children"),
    Output(ID_NEW_NOTE_STORE, "data"),
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
