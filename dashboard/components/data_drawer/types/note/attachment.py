from pprint import pprint

import dash
import dash_mantine_components as dmc
from dash import Output, Input, State, html, dcc, ALL, MATCH
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from configuration import PRIMARY_COLOR
from dashboard.components.button.components.action_button import action_button
from dashboard.components.data_drawer.types.note.form_view import note_form
from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id_config import *
from dashboard.maindash import app
from dashboard.model.file import File
from dashboard.model.note import Note
from dashboard.util.user_validation import get_user_from_cookies
from dashboard.util.util import pretty_date
from util.helper_functions import safe_reduce


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
