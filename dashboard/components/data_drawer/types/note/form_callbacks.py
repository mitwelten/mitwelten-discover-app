import dash
from dash import Output, Input, State, html, ALL, MATCH
from dash.exceptions import PreventUpdate

from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.id import *
from dashboard.maindash import app
from dashboard.util.user_validation import get_user_from_cookies


# enable and disable marker clicks to the notes marker to support move operations
@app.callback(
    Output({"role": "Notes", "id": MATCH, "label": "Prevent Marker Event"}, "data"),
    Input({"role": "Notes", "id": MATCH, "label": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def set_marker_icon_draggable(click):
    print("set_marker_icon_draggable", dash.ctx.triggered_id)
    print("activate prevent marker click: ", click)
    trigger = dash.ctx.triggered_id
    match trigger["label"]:
        case "Edit Button":
            print("Edit Button Pressed")
            return dict(state=True)
        case "Save Button":
            return dict(state=False)
        case "Cancel Button":
            return dict(state=False)
    raise PreventUpdate



# change the note marker icon to display move support
@app.callback(
    Output({"role": "Notes", "id": MATCH, "label": "Node", "lat": ALL, "lon": ALL}, "icon"),
    Output({"role": "Notes", "id": MATCH, "label": "Node", "lat": ALL, "lon": ALL}, "draggable"),
    Input({"role": "Notes", "id": MATCH, "label": "Prevent Marker Event"}, "data"),
    prevent_initial_call=True
)
def change_note_icon(store_data):
    print("change_note_icon", dash.ctx.triggered_id)
    print("change note icon", store_data)
    if store_data["state"]:
        return [dict(iconUrl="assets/markers/note_move.svg", iconAnchor=[60, 50], iconSize=120)], [True]
    return [dict(iconUrl="assets/markers/note.svg", iconAnchor=[15, 6], iconSize=30)], [False]
