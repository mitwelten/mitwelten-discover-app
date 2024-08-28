from dash import Output, Input, ALL, State, ctx, no_update
from dash.exceptions import PreventUpdate
from pprint import pprint

from src.config.id_config import *
from src.config.map_config import MAPS, OVERLAYS, MAP_TYPES
from src.main import app
from src.util.helper_functions import safe_reduce
from src.url.parse import update_query_data

def update_store(store, collection):
    index_map = store["index"]
    new_map = next(x for x in collection if x.index == index_map)
    if new_map is None:
        return no_update, no_update
    return new_map.source, new_map.source_attribution


@app.callback(
    Output(ID_BASE_LAYER_MAP, "url"),
    Output(ID_BASE_LAYER_MAP, "attribution"),
    Input(ID_BASE_MAP_STORE, "data"),
)
def handle_map_store_update(store):
    return update_store(store, MAPS)


@app.callback(
    Output(ID_OVERLAY_MAP, "url"),
    Output(ID_OVERLAY_MAP, "attribution"),
    Output(ID_AFFIX_LEBENSRAUM_LEGENDE, "display"),
    Input(ID_OVERLAY_MAP_STORE, "data"),
)
def handle_overlay_store_update(store):
    display = "none"
    if store["index"] == 1:
        display = "block"
    [src, attr] = update_store(store, OVERLAYS)
    return src, attr, display


def handle_map_update(_):
    if ctx.triggered_id is None:
        return no_update
    return {"index": ctx.triggered_id["index"]}


@app.callback(
    Output(ID_BASE_MAP_STORE, "data"),
    Input({'role': MAP_TYPES[0], 'index': ALL, 'place': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def handle_map_update_base(clicks):
    if ctx.triggered_id is None:
        raise PreventUpdate
    if clicks is None or clicks == 0:
        return no_update

    return {"index": ctx.triggered_id["index"]}


@app.callback(
    Output(ID_OVERLAY_MAP_STORE, "data"),
    Input({'role': MAP_TYPES[1], 'index': ALL, 'place': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def handle_map_update_overlay(clicks):
    if ctx.triggered_id is None:
        raise PreventUpdate
    if clicks is None or clicks == 0:
        return no_update

    return {"index": ctx.triggered_id["index"]}


def update_map_icon(data, children, icons):
    map_id = data["index"]
    for child in children:
        # nested: Div - Stack - Div
        child["props"]["children"][0]["props"]["className"] = ""

    children[map_id]["props"]["children"][0]["props"]["className"] = "map-image-selected"

    for icon in icons:
        icon["props"]["className"] = ""

    icons[map_id]["props"]["className"] = "map-image-selected"
    return icons, children


for map_type in MAP_TYPES:
    app.callback(
            Output({'role': map_type, 'index': ALL, 'place': "menu"}, 'leftSection'),
            Output({'role': map_type, 'index': ALL, 'place': "drawer"}, 'children'),
            Input({'role': "map_store", 'type': map_type}, "data"),
            State({'role':  map_type, 'index': ALL, 'place': "drawer"}, 'children'),
            State({'role':  map_type, 'index': ALL, 'place': "menu"}, 'leftSection'),
    )(update_map_icon)



@app.callback(
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_BASE_MAP_STORE, "data"),
    Input(ID_OVERLAY_MAP_STORE, "data"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
)
def update_fs_tag_in_url_params(map, overlay, data):
    map_index = map["index"] or 0
    overlay_index = overlay["index"] or 0

    return update_query_data(data, {"map": map_index, "overlay": overlay_index})
