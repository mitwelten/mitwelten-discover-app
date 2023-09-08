from dash import Output, Input
from dash.exceptions import PreventUpdate

from dashboard.config.id import *
from dashboard.maindash import app


# switch drawer content to detail view
@app.callback(
    Output(ID_NOTE_FORM_VIEW, "style", allow_duplicate=True),
    Output(ID_NOTE_DETAIL_VIEW, "style", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_NOTE_EDIT_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def update_note_container_content(click):
    if click is None or click == 0:
        raise PreventUpdate
    return {"display": "block"}, {"display": "none"}, False, dict(state=True)


# switch drawer content to note form
@app.callback(
    Output(ID_NOTE_FORM_VIEW, "style", allow_duplicate=True),
    Output(ID_NOTE_DETAIL_VIEW, "style", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "withCloseButton", allow_duplicate=True),
    Output(ID_PREVENT_MARKER_EVENT, "data", allow_duplicate=True),
    Input(ID_NOTE_FORM_SAVE_BUTTON, "n_clicks"),
    Input(ID_NOTE_FORM_CANCEL_BUTTON, "n_clicks"),
    prevent_initial_call=True
)
def update_layout_from_save_button_click(save_click, cancel_click):
    if save_click is None or save_click == 0:
        if cancel_click is None or cancel_click == 0:
            raise PreventUpdate
    return {"display": "none"}, {"display": "block"}, True, dict(state=False)



# @app.callback(
#     # Output(ID_NOTES_LAYER_GROUP, "children"),
#     Output(ID_NEW_NOTE_STORE, "data", allow_duplicate=True),
#     Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
#     Input(ID_MAP, "dbl_click_lat_lng"),
#     # State(ID_NOTES_LAYER_GROUP, "children"),
#     prevent_initial_call=True
# )
# def handle_double_click(click):
#     user = get_user_from_cookies()
#     if user is None:
#         notification = create_notification(
#             "Operation not permitted",
#             "Log in to create notes!",
#             NotificationType.WARN
#         )
#         return dash.no_update, notification
#
#     # marker = dl.Marker(
#     #     position=[click[0], click[1]],
#     #     icon=dict(iconUrl="assets/markers/note.svg", iconAnchor=[15, 6], iconSize=30),
#     # )
#     # if markers is None:
#     #     markers = []
#     # return [*markers, marker], dict(lat=click[0], lon=click[1]), dash.no_update,
#     return dict(lat=click[0], lon=click[1]), dash.no_update




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


