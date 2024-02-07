import dash_mantine_components as dmc
from dash import html, dcc, dash, Output, Input, State
from dash.exceptions import PreventUpdate

from src.main import app
from src.config.id_config import *
from src.components.button.components.action_button import action_button
from src.util.user_validation import get_user_from_cookies

def attachment_modal(note, editable=False):
    return dmc.Modal(
            title="Attachments",
            id=ID_ATTACHMENT_FORM_MODAL,
            zIndex=10000,
            children=[attachment_table(note, editable)]
    )


def attachment_table(note, is_editable=False):
    user = get_user_from_cookies()
    header = [
        html.Thead(
            html.Tr([
                html.Th("Name"),
                html.Th("Type"),
                html.Th("Last Modified"),
                html.Th(""),
            ])
        )
    ]

    rows = []
    for file in note.files:
        rows.append(
            html.Tr([
                html.Td(file.name),
                html.Td(file.type),
                html.Td(file.object_name),
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




@app.callback(
    Output(ID_ATTACHMENT_FORM_MODAL, "opened"),
    #Output("id-image-container", "children"),
    Input(ID_NOTE_ATTACHMENT_BUTTON, "n_clicks"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def update_attachment_modal_state(click, note):
    if click == 0 or click is None:
        raise PreventUpdate

    # auth_cookie = flask.request.cookies.get("auth")
    # file = get_file("test_img.png", auth_cookie)
    return True


# @app.callback(
#     Output(ID_ALERT_INFO, "is_open", allow_duplicate=True),
#     Output(ID_ALERT_INFO, "children", allow_duplicate=True),
#     Input(ID_NOTE_ATTACHMENT_BUTTON, "n_clicks"),
#     prevent_initial_call=True
# )
# def handle_attachment_click(click):
#     print("handle att click")
#     if click == 0 or click is None:
#         raise PreventUpdate
# 
#     auth_cookie = flask.request.cookies.get("auth")
#     img = get_image( "https://picsum.photos/200", auth_cookie)
#     print("img", img)
#     notification = [
#         dmc.Title("Sorry, Feature not implemented yet!", order=6),
#         dmc.Text("Attachments coming soon...")
#     ]
# 
#     return True, notification
# def parse_contents(content, name, date):
#     return dict(content=content, name=name, date=date)
#
#
# @app.callback(
#     Output(ID_NEW_NOTE_STORE, 'data'),
#     Input('upload-image', 'contents'),
#     State('upload-image', 'filename'),
#     State('upload-image', 'last_modified'),
#     State(ID_NEW_NOTE_STORE, 'data')
# )
# def update_output(list_of_contents, list_of_names, list_of_dates, store):
#     if list_of_contents is not None:
#         content = [
#             parse_contents(c, n, d) for c, n, d in
#             zip(list_of_contents, list_of_names, list_of_dates)]
#         for c in content:
#             store.append(c)
#     return store
#
#
# @app.callback(
#     Output('output-image-upload', "children"),
#     Input(ID_NEW_NOTE_STORE, "data"),
#     prevent_initial_call=True
# )
# def show_new_notes_from_store(data):
#     all_note_titles = []
#     for note in data:
#         all_note_titles.append(html.Div(note["name"]))
#     return all_note_titles
