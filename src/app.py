import time
from functools import partial
import pprint

from six import viewvalues
from src.model.note import Note

import dash_leaflet as dl
import dash_mantine_components as dmc
import dash_core_components as dcc
from dash import (
    clientside_callback,
    ClientsideFunction,
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
    ID_NOTES_LAYER_GROUP,
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
    ID_BROWSER_PROPERTIES_STORE,
    ID_SETTINGS_DRAWER,
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


clientside_callback(
    ClientsideFunction(
        namespace="browser_properties", function_name="fetchWindowProps"
    ),
    Output(ID_BROWSER_PROPERTIES_STORE, "data"),
    Input(ID_SELECTED_MARKER_STORE, "data"),
)





@app.callback(
    Output(ID_MAP, "viewport", allow_duplicate=True),
    Input(ID_BROWSER_PROPERTIES_STORE, "data"),
    State(ID_SETTINGS_DRAWER, "opened"),
    State(ID_SETTINGS_DRAWER, "size"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_SELECTED_MARKER_STORE, "data"),
    State(ID_MAP, "bounds"),
    State(ID_MAP, "zoom"),
    State(ID_MAP, "center"),
    prevent_initial_call=True,
)
def ensure_marker_visibility_in_viewport(
    browser_props,
    drawer_state,
    settings_drawer_size,
    data_drawer_size,
    marker,
    bounds,
    zoom,
    center,
):
    if marker is None:
        raise PreventUpdate

    top    = bounds[1][0]
    bottom = bounds[0][0]
    left   = bounds[0][1]
    right  = bounds[1][1]

    # visibile map distance in grad
    map_delta_lat = top - bottom
    map_delta_lon = right - left

    # set drawer size to 1 if the settings drawer is closed
    settings_drawer_size = 1 if not drawer_state else settings_drawer_size

    # the height of the data drawer in grad
    data_drawer_height = map_delta_lat   / browser_props["height"] * data_drawer_size

    # the width of the settings drawer in grad
    settings_drawer_width = map_delta_lon / browser_props["width"]  * settings_drawer_size

    # the range, in which markers are moved to the center in %
    moving_zone_bounds = [[10, 20],[30, 20]] 

    zone_factor_h = (top - (bottom + data_drawer_height)) / 100
    zone_factor_w = (right - (left + settings_drawer_width)) / 100

    ok_zone = [
        [bottom + data_drawer_height + moving_zone_bounds[0][0] * zone_factor_h, left + settings_drawer_width + moving_zone_bounds[0][1] * zone_factor_w],
        [top - moving_zone_bounds[1][0] * zone_factor_h, right -  moving_zone_bounds[1][1] * zone_factor_w]
         ]

    pprint.pprint(marker)

    marker_loc = marker["data"]["location"]

    # returns an array containing the values to be moved: [[bottom/top], [left/right]]
    def check_marker_pos(marker_loc, ok_zone):
        overlapping = [0,0]
        # bottom
        if marker_loc["lat"] < ok_zone[0][0]: 
            overlapping[0] = ok_zone[0][0] - marker_loc["lat"]
        # top
        if marker_loc["lat"] > ok_zone[1][0]: 
            overlapping[0] = ok_zone[1][0] - marker_loc["lat"]
        # left
        if marker_loc["lon"] < ok_zone[0][1]:
            overlapping[1] = ok_zone[0][1] - marker_loc["lon"]
        # right
        if marker_loc["lon"] > ok_zone[1][1]:
            overlapping[1] = ok_zone[1][1] - marker_loc["lon"]
        return overlapping

    move_required = check_marker_pos(marker_loc, ok_zone)

    new_center = [center["lat"] + (move_required[0] * -1), center["lng"] + (move_required[1] * -1)]

    return dict(center=new_center, zoom=zoom, transition="flyTo")
