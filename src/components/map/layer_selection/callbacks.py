from dash import Output, Input, ALL, State, ctx, no_update

from src.config.id_config import *
from src.config.map_config import MAPS, OVERLAYS, MAP_TYPES
from src.main import app
from src.util.helper_functions import safe_reduce


def update_store(store, collection):
    index_map = store["index"]
    new_map = next(x for x in collection if x.index == index_map)
    if new_map is None:
        return no_update
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
    Input(ID_OVERLAY_MAP_STORE, "data"),
)
def handle_overlay_store_update(store):
    return update_store(store, OVERLAYS)


def handle_map_update(_):
    if ctx.triggered_id is None:
        return no_update
    return {"index": ctx.triggered_id["index"]}


@app.callback(
    Output(ID_BASE_MAP_STORE, "data"),
    Input({'role': MAP_TYPES[0], 'index': ALL, 'place': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def handle_map_update_0(clicks):
    clicks = safe_reduce(lambda x, y: x + y, clicks, 0)
    if clicks is None or clicks == 0:
        return no_update

    return {"index": triggered_id["index"]}


@app.callback(
    Output(ID_OVERLAY_MAP_STORE, "data"),
    Input({'role': MAP_TYPES[1], 'index': ALL, 'place': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def handle_map_update_1(clicks):
    clicks = safe_reduce(lambda x, y: x + y, clicks, 0)
    if clicks is None or clicks == 0:
        return no_update

    return {"index": ctx.triggered_id["index"]}


def update_map_icon(data, children, icons):
    map_id = data["index"]
    for child in children:
        # nestet: Div - Stack - Div
        child["props"]["children"][0]["props"]["className"] = ""

    children[map_id]["props"]["children"][0]["props"]["className"] = "map-image-selected"

    for icon in icons:
        icon["props"]["className"] = ""

    icons[map_id]["props"]["className"] = "map-image-selected"
    return icons, children


for map_type in MAP_TYPES:
    app.callback(
            Output({'role': map_type, 'index': ALL, 'place': "menu"}, 'icon'),
            Output({'role': map_type, 'index': ALL, 'place': "drawer"}, 'children'),
            Input({'role': "map_store", 'type': map_type}, "data"),
            State({'role':  map_type, 'index': ALL, 'place': "drawer"}, 'children'),
            State({'role':  map_type, 'index': ALL, 'place': "menu"}, 'icon'),
    )(update_map_icon)
