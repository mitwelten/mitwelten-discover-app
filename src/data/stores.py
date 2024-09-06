import flask
from dash.exceptions import PreventUpdate
from dash import Output, Input, State, ctx


from src.components.data_drawer.types.pollinator import *
from src.config.map_config import SOURCE_PROPS, get_source_props
from src.data.init import init_notes, init_tags
from src.main import app
from src.url.parse import update_query_data


def stores(args, deployments, notes, env_data, tags, active_depl):
    all_sources = [
            source for source in SOURCE_PROPS.keys() 
            if get_source_props(source)["type"] == "physical"
            ]

    return[*[
        dcc.Store(
            id={"role": source_type, "label": "Store", "type": "physical"},
            data=dict(entries=deployments[source_type], type=source_type))
        for source_type in all_sources
        ],

           dcc.Store(
               id={"role": "Note", "label": "Store", "type": "virtual"}, 
               data=dict(entries=notes)),
           dcc.Store(
               id={"role": "Environment", "label": "Store", "type": "virtual"}, 
               data=dict(entries=env_data["entries"], legend=env_data["legend"])),

           dcc.Store(
               id=ID_TAG_DATA_STORE,           
               data=dict(all=tags)),

           dcc.Store(id=ID_DEPLOYMENT_DATA_STORE,    data=deployments),
           dcc.Store(id=ID_SELECTED_MARKER_STORE,    data=dict(data=active_depl, type=active_depl.get("node", {}).get("type") if active_depl else None)),
           dcc.Store(id=ID_BASE_MAP_STORE,           data=dict(index=args["map"]), storage_type="local"),
           dcc.Store(id=ID_OVERLAY_MAP_STORE,        data=dict(index=args["overlay"]), storage_type="local"),
           dcc.Store(id=ID_PREVENT_MARKER_EVENT,     data=dict(state=False)),
           dcc.Store(id=ID_EDIT_NOTE_STORE,          data=dict(data=None)),
           dcc.Store(id=ID_BROWSER_PROPERTIES_STORE, data=None, storage_type="local"),
           dcc.Store(id=ID_QUERY_PARAM_STORE,        data=args),
           dcc.Store(id=ID_TIMEZONE_STORE),
           ]

@app.callback(
    Output({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    Input ({"role": "Note", "label": "Store", "type": "virtual"}, "data"),
    prevent_initial_call=True,
)
def refresh_notes_from_backend(data):
    print("refresh_notes_from_backend", data)

    if ctx.triggered_id == None:
        raise PreventUpdate

    if data is None or data["entries"] == []:
        print("refreshing notes")
        cookies = flask.request.cookies
        data["entries"] = init_notes(cookies["auth"] if cookies else None)
        return data
    else:
        raise PreventUpdate


@app.callback(
    Output(ID_TAG_DATA_STORE, "data"),
    Input (ID_TAG_DATA_STORE, "data"),
    prevent_initial_call=True,
)
def refresh_tags_from_backend(data):
    if ctx.triggered_id == None:
        raise PreventUpdate
    if data is None:
        data = {}
        data["all"] = init_tags()
        return data
    else:
        raise PreventUpdate


@app.callback(
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_SELECTED_MARKER_STORE, "data"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
    )
def update_url(marker, data):
    if marker is None:
        raise PreventUpdate

    if marker["type"] == "Note":
        name = "note_id"
        id = marker["data"]["id"]
    elif marker["type"] == "Environment":
        name = "env_id"
        id = marker["data"]["id"]
    else:
        name = "node_label"
        id = marker["data"]["node"]["node_label"]

    update_query_data(
            data, 
            {
                "node_label": None,
                "note_id": None,
                "env_id": None,
             }
            )
    return update_query_data(data, {name: id})

