import time
from functools import partial
import pprint


import dash_mantine_components as dmc
import dash_core_components as dcc
from dash import (
    ALL,
    html,
    Output,
    Input,
    State, 
    ctx,
    no_update,
)
from dash.exceptions import PreventUpdate

from src.components.alert.alert import alert_danger, alert_warning, alert_info
from src.components.button.buttons import control_buttons
from src.config.id_config import (
    ID_STAY_LOGGED_IN_INTERVAL,
    ID_LOGO_CONTAINER,
    ID_CONFIRM_UNSAVED_CHANGES_DIALOG,
    ID_CONFIRM_DELETE_DIALOG,
    ID_NOTE_ATTACHMENT_MODAL,
    ID_URL_LOCATION,
    ID_APP_CONTAINER,
    ID_APP_THEME,
    ID_LOGIN_AVATAR_CONTAINER,
    ID_MAP,
    ID_SELECTED_MARKER_STORE,
    ID_PREVENT_MARKER_EVENT,
    ID_CHART_DRAWER,
    ID_SELECTED_NOTE_STORE,
)
from src.components.map.init_map import map_figure
from src.components.settings_drawer.settings_drawer import settings_drawer
from src.components.data_drawer.data_drawer import chart_drawer
from src.config.app_config import (
    app_theme,
    CONFIRM_UNSAVED_CHANGES_MESSAGE,
    CONFIRM_DELETE_MESSAGE,
)
from src.config.map_config import SOURCE_PROPS
from src.data.stores import stores
from src.util.helper_functions import safe_reduce
from src.util.user_validation import get_expiration_date_from_cookies
from src.main import app

from src.components.data_drawer.types.note import callbacks


app_content = [
    dcc.Interval(id=ID_STAY_LOGGED_IN_INTERVAL, interval=30 * 1000, disabled=True),
    alert_danger,
    alert_warning,
    alert_info,
    *stores,
    html.Div(
        html.A(
            "MITWELTEN",
            title="mitwelten.org",
            href="https://mitwelten.org",
            target="_blank",
            className="mitwelten-logo",
        ),
        id=ID_LOGO_CONTAINER,
    ),
    # dmc.MediaQuery(
    #     html.Div(
    #         dmc.Select(
    #             id=ID_DEPLOYMENT_SELECT_SEARCH_BAR,
    #             allowDeselect=True,
    #             data=[],
    #             placeholder="Search for Deployments",
    #             searchable=True,
    #             nothingFound="ID not found",
    #             style={"width": "300px"},
    #             size="md",
    #             radius="xl",
    #             icon=DashIconify(icon="material-symbols:search", width=20),
    #             rightSection=dmc.ActionIcon(
    #                 DashIconify(icon="material-symbols:my-location", width=20),
    #                 size="lg",
    #                 variant="subtle",
    #                 id=ID_SEARCHBAR_SEARCH_DEPLOYMENT_BUTTON,
    #                 n_clicks=0,
    #                 color=PRIMARY_COLOR,
    #             ),
    #         ),
    #         id="id-search-bar-container"
    #     ),
    #     smallerThan="md",
    #     styles={"display": "none"}
    # ),
    dcc.ConfirmDialog(
        id=ID_CONFIRM_UNSAVED_CHANGES_DIALOG, message=CONFIRM_UNSAVED_CHANGES_MESSAGE
    ),
    dcc.ConfirmDialog(id=ID_CONFIRM_DELETE_DIALOG, message=CONFIRM_DELETE_MESSAGE),
    map_figure,
    chart_drawer,
    *control_buttons,
    settings_drawer,
    dmc.Modal(id=ID_NOTE_ATTACHMENT_MODAL, size="lg", opened=False, zIndex=30000),
    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
]

attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
discover_app = dmc.MantineProvider(
    id=ID_APP_THEME,
    theme=app_theme,
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        html.Div(children=app_content, id=ID_APP_CONTAINER),
    ],
)

app.layout = discover_app


@app.callback(
    Output(ID_STAY_LOGGED_IN_INTERVAL, "interval"),
    Output(ID_LOGIN_AVATAR_CONTAINER, "n_clicks"),
    Input(ID_STAY_LOGGED_IN_INTERVAL, "n_intervals"),
    State(ID_LOGIN_AVATAR_CONTAINER, "n_clicks"),
    prevent_initial_call=True,
)
def create_backend_request_to_stay_logged_in(_, avatar_clicks):
    exp = get_expiration_date_from_cookies()
    if exp is None or exp - time.time() < 0:
        return no_update, avatar_clicks + 1 if avatar_clicks is not None else 0
    raise PreventUpdate


@app.callback(
    Output(ID_URL_LOCATION, "search"),
    Input(ID_MAP, "clickData"),
    Input(ID_MAP, "zoom"),
    prevent_initial_call=True,
)
def map_click_handle(click_data, zoom):
    loc = ""
    if click_data is not None:
        loc = f"?lat={click_data['latlng']['lat']}&lon={click_data['latlng']['lng']}&zoom={zoom}"
    return loc


def handle_marker_click(data_source, marker_click, prevent_event, store, clickdata):
    if prevent_event["state"]:
        raise PreventUpdate

    click_sum = safe_reduce(lambda x, y: x + y, marker_click, 0)
    if click_sum == 0:
        raise PreventUpdate

    for entry in store[0]["entries"]:
        if entry["id"] == ctx.triggered_id["id"]:
            return dict(data=entry, type=data_source)

    raise PreventUpdate


for source in SOURCE_PROPS.keys():
    app.callback(
        Output(ID_SELECTED_MARKER_STORE, "data", allow_duplicate=True),
        Input({"role": source, "id": ALL, "label": "Node"}, "n_clicks"),
        State(ID_PREVENT_MARKER_EVENT, "data"),
        State({"role": source, "label": "Store", "type": ALL}, "data"),
        State({"role": source, "id": ALL, "label": "Node"}, "clickData"),
        prevent_initial_call=True,
    )(partial(handle_marker_click, source))


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_MAP, "clickData"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True,
)
def map_click(_, selected_note):
    if selected_note["data"] is None:
        return False, no_update, no_update

    if selected_note["isDirty"]:
        return no_update, True, no_update

    return False, no_update, dict(data=None, inEditMode=False, isDirty=False)


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Input(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "submit_n_clicks"),
    prevent_initial_call=True,
)
def deactivate_edit_mode(cancel_click):
    if cancel_click is None or cancel_click == 0:
        raise PreventUpdate
    return dict(data=None, inEditMode=False), False


