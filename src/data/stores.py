from functools import partial

import flask
from dash.exceptions import PreventUpdate

from src.components.data_drawer.types.pollinator import *
from src.config.map_config import SOURCE_PROPS, get_source_props
from src.data.init import init_deployment_data, init_environment_data, init_notes, init_tags
from src.main import app

stores = [
    *[dcc.Store(
        {"role": source_type, "label": "Store", "type": get_source_props(source_type)["type"]},
        data=dict(entries=[], type=source_type))
        for source_type in SOURCE_PROPS.keys()
    ],
    *[dcc.Store(f"id-{source_type}-refresh-store", data=dict(pending=False))
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
]

@app.callback(
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    Input ({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    Input("id-Note-refresh-store", "data")
)
def load_notes_from_backend(data, _):
    outdated = True # TODO: implement
    if outdated:
        cookies = flask.request.cookies
        data["entries"] = init_notes(cookies["auth"] if cookies else None)
        return data
    else:
        raise PreventUpdate


@app.callback(
    Output({"role": "Environment Data Point", "label": "Store", "type": "virtual"}, "data"),
    Input ({"role": "Environment Data Point", "label": "Store", "type": "virtual"}, "data"),
)
def load_env_from_backend(data):
    outdated = False  # TODO: implement data update
    if data["entries"] == [] or outdated:
        data["entries"], data["legend"] = init_environment_data()
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
def load_deployments_from_backend(data):
    outdated = False  # TODO: implement data update
    if data is None or outdated:
        return init_deployment_data()
    raise PreventUpdate


def update_deployment_store(source_type, data):
    source_data = data[source_type] if data.get(source_type) is not None else []
    return dict(entries=source_data, type=source_type)

for source in SOURCE_PROPS.keys():
    if get_source_props(source)["type"] == "physical":
        app.callback(
            Output({"role": source, "label": "Store", "type": "physical"}, "data"),
            Input(ID_DEPLOYMENT_DATA_STORE, "data"),
            prevent_initial_call=True
        )(partial(update_deployment_store, source))
