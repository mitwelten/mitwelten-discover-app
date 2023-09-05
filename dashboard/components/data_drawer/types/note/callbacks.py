import dash
from dash import Output, Input, State, html, ALL, MATCH
from dash.exceptions import PreventUpdate

from dashboard.components.data_drawer.types.note.detail_view import note_detail_view
from dashboard.components.data_drawer.types.note.form_view import note_form
from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.util.user_validation import get_user_from_cookies


@app.callback(
    Output("id-note-container", "children", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input({"role": "Notes", "id": ALL, "label": ALL}, "n_clicks"),
    State("id-current-note-store", "data"),
    prevent_initial_call=True
)
def update_note_container_content(click, data):
    trigger = dash.ctx.triggered_id
    match trigger["label"]:
        case "Edit Button":
            return note_form(data["note"]), False, dict(state=True)
        case _:
            return note_detail_view(data["note"]), True, dict(state=False)


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
