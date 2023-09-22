from functools import partial
from pprint import pprint

import dash
import flask
from dash import clientside_callback, ClientsideFunction, ALL
from dash.exceptions import PreventUpdate

from dashboard.components.button.buttons import control_buttons
from dashboard.components.data_drawer.data_drawer import chart_drawer
from dashboard.components.data_drawer.types.pollinator import *
from dashboard.components.map.init_map import map_figure
from dashboard.components.settings_drawer.settings_drawer import settings_drawer
from dashboard.config.app_config import app_theme
from dashboard.config.map_config import SOURCE_PROPS, get_source_props
from dashboard.init import init_deployment_data, init_environment_data, init_notes, init_tags
from dashboard.maindash import app
from dashboard.util.helper_functions import safe_reduce, ensure_marker_visibility

deployments = init_deployment_data()

app_content = [
    dcc.Location(id=ID_URL_LOCATION, refresh=False, search=""),
    *[dcc.Store(
        {"role": source_type, "label": "Store", "type": get_source_props(source_type)["type"]},
        data=dict(entries=[], type=source_type), storage_type="local")
        for source_type in SOURCE_PROPS.keys()
    ],
    dcc.Store(id=ID_DEPLOYMENT_DATA_STORE,    data=None),
    dcc.Store(id=ID_TAG_DATA_STORE,           data=None),
    dcc.Store(id=ID_SELECTED_MARKER_STORE,    data=None),
    dcc.Store(id=ID_BASE_MAP_STORE,           data=dict(index=0), storage_type="local"),
    dcc.Store(id=ID_OVERLAY_MAP_STORE,        data=dict(index=0), storage_type="local"),
    dcc.Store(id=ID_PREVENT_MARKER_EVENT,     data=dict(state=False)),
    dcc.Store(id=ID_SELECTED_NOTE_STORE,      data=dict(data=None, inEditMode=False, isDirty=False)),
    dcc.Store(id=ID_BROWSER_PROPERTIES_STORE, data=None, storage_type="local"),

    html.Div(
        html.A(
            "MITWELTEN",
            title="mitwelten.org",
            href="https://mitwelten.org",
            target="_blank",
            className="mitwelten-logo"
        ),
        id=ID_MAP_CONTAINER,
    ),

    dcc.ConfirmDialog(
        id=ID_CONFIRM_UNSAVED_CHANGES_DIALOG,
        message="You have unsaved changes. Do you want to discard them?"
    ),
    map_figure,
    chart_drawer(),
    *control_buttons(),
    settings_drawer(deployments),
    dmc.Modal(id=ID_NOTE_ATTACHMENT_MODAL, size="lg", opened=False, zIndex=30000),
]


discover_app = dmc.MantineProvider(
    id=ID_APP_THEME,
    theme=app_theme,
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        dmc.NotificationsProvider([
            html.Div(id=ID_NOTIFICATION_CONTAINER),
            html.Div(
                children=app_content,
                id=ID_APP_CONTAINER,
            )
        ],
            zIndex=9999999
        )
    ]
)

app.layout = discover_app


@app.callback(
    Output(ID_URL_LOCATION, "search"),
    Input(ID_MAP, "click_lat_lng"),
    Input(ID_MAP, "zoom"),
    prevent_initial_call=True
)
def map_click(click_lat_lng, zoom):
    loc = ""
    if click_lat_lng is not None:
        loc = f"?lat={click_lat_lng[0]}&lon={click_lat_lng[1]}&zoom={zoom}"
    return loc


def handle_marker_click(data_source, marker_click, prevent_event, store):
    if prevent_event["state"]:
        raise PreventUpdate

    click_sum = safe_reduce(lambda x, y: x + y, marker_click, 0)
    if click_sum == 0:
        raise PreventUpdate

    for entry in store[0]["entries"]:
        if entry["id"] == dash.ctx.triggered_id["id"]:
            return dict(data=entry, type=data_source)

    raise PreventUpdate


for source in SOURCE_PROPS.keys():
    app.callback(
        Output(ID_SELECTED_MARKER_STORE, "data", allow_duplicate=True),
        Input({"role": source, "id": ALL, "label": "Node"}, "n_clicks"),
        State(ID_PREVENT_MARKER_EVENT, "data"),
        State({"role": source, "label": "Store", "type": ALL}, "data"),
        prevent_initial_call=True
    )(partial(handle_marker_click, source))


@app.callback(
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Output(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "displayed", allow_duplicate=True),
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Input(ID_MAP, "click_lat_lng"),
    State(ID_SELECTED_NOTE_STORE, "data"),
    prevent_initial_call=True
)
def map_click(_, selected_note):
    if selected_note["data"] is None:
        return False, dash.no_update, dash.no_update

    if selected_note["isDirty"]:
        return dash.no_update, True, dash.no_update

    return False, dash.no_update, dict(data=None, inEditMode=False, isDirty=False)


@app.callback(
    Output(ID_SELECTED_NOTE_STORE, "data", allow_duplicate=True),
    Output(ID_CHART_DRAWER, "opened", allow_duplicate=True),
    Input(ID_CONFIRM_UNSAVED_CHANGES_DIALOG, "submit_n_clicks"),
    prevent_initial_call=True
)
def deactivate_edit_mode(cancel_click):
    if cancel_click is None or cancel_click == 0:
        raise PreventUpdate
    return dict(data=None, inEditMode=False), False


clientside_callback(
    ClientsideFunction(
        namespace="browser", function_name="testFunction"
    ),
    Output(ID_BROWSER_PROPERTIES_STORE, "data"),
    Input (ID_SELECTED_MARKER_STORE,    "data"),
)

@app.callback(
    Output(ID_MAP, "center"),
    Input(ID_BROWSER_PROPERTIES_STORE, "data"),
    State(ID_SETTINGS_DRAWER, "opened"),
    State(ID_SETTINGS_DRAWER, "size"),
    State(ID_CHART_DRAWER, "size"),
    State(ID_SELECTED_MARKER_STORE, "data"),
    State(ID_MAP, "bounds"),
    State(ID_MAP, "viewport"),
)
def ensure_marker_visibility_in_viewport(
        browser_props,
        drawer_state,
        settings_drawer_size,
        data_drawer_size,
        marker,
        bounds,
        viewport
):
    if marker is None:
        raise PreventUpdate

    marker_position = marker["data"]["location"]
    map_center = viewport["center"]
    new_center = ensure_marker_visibility(
        map_center,
        bounds,
        marker_position,
        browser_props,
        settings_drawer_size if drawer_state else 0,  # settings drawer is open or not
        data_drawer_size,
    )
    return new_center


@app.callback(
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    Input ({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
)
def load_notes_from_backend(data):
    outdated = False
    if data["entries"] == [] or outdated:
        cookies = flask.request.cookies
        data["entries"] = init_notes(cookies["auth"] if cookies else None)
        return data
    else:
        raise PreventUpdate


@app.callback(
    Output({"role": "Environment Data Point", "label": "Store", "type": "virtual"}, "data"),
    Input ({"role": "Environment Data Point", "label": "Store", "type": "virtual"}, "data"),
)
def load_notes_from_backend(data):
    outdated = False  # TODO: implement data update
    if data["entries"] == [] or outdated:
        data["entries"], data["legend"]= init_environment_data()
        return data
    raise PreventUpdate


@app.callback(
    Output(ID_TAG_DATA_STORE, "data"),
    Input (ID_TAG_DATA_STORE, "data")
)
def load_tags_from_backend(data):
    outdated = False  # TODO: implement data update
    if data is None or outdated:
        return init_tags()
    raise PreventUpdate


@app.callback(
    Output(ID_DEPLOYMENT_DATA_STORE, "data"),
    Input (ID_DEPLOYMENT_DATA_STORE, "data")
)
def load_tags_from_backend(data):
    outdated = False  # TODO: implement data update
    if data is None or outdated:
        return init_deployment_data()
    raise PreventUpdate


def update_deployment_store(source_type, data):
    return dict(entries=data[source_type], type=source_type)

for source in SOURCE_PROPS.keys():
        if get_source_props(source)["type"] == "physical":
            app.callback(
                Output({"role": source, "label": "Store", "type": "physical"}, "data"),
                Input(ID_DEPLOYMENT_DATA_STORE, "data"),
                prevent_initial_call=True
            )(partial(update_deployment_store, source))
