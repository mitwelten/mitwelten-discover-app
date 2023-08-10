import dash
import dash_mantine_components as dmc
from dash import html, Output, Input, ALL, State

from dashboard.components.button.components.action_button import action_button
from dashboard.config.id import *
from dashboard.config.map import MAPS, OVERLAYS
from dashboard.maindash import app


MAP_TYPES = ["base", "overlay"]


def map_menu_popup(id_prefix):
    menu_entries = [dmc.MenuLabel("Map")]

    for map_config in MAPS:
        menu_entries.append(
            dmc.MenuItem(
                map_config.title,
                icon=html.Div(
                    dmc.Image(src=map_config.image, alt="map", width=48, height=48, radius=5),
                    # className="map-image-selected" if map_config.index == 0 else ""
                ),
                id={'role': "base", 'index': map_config.index, 'place': id_prefix},
            )
        )
    menu_entries.append(dmc.MenuDivider())
    menu_entries.append(dmc.MenuLabel("Overlays"))

    for overlay_config in OVERLAYS:
        menu_entries.append(
            dmc.MenuItem(
                overlay_config.title,
                icon=html.Div(
                    dmc.Image(src=overlay_config.image, alt="map", width=48, height=48, radius=5),
                    # className="map-image-selected" if overlay_config.index == 0 else ""
                ),
                id={'role': MAP_TYPES[1], 'index': overlay_config.index, 'place': id_prefix},
            )
        )

    return dmc.Menu(
        [
            dmc.MenuTarget(action_button(icon="material-symbols:layers-outline")),
            dmc.MenuDropdown(menu_entries),
        ],
        trigger="hover",
        className="map-menu",
        transition="scale-y",
        transitionDuration=100,
        position="bottom-end",
        withArrow=True,
        arrowSize=10,
        arrowOffset=15,
        zIndex=500000
    )


def map_menu_drawer(id_prefix):
    return dmc.Container(
        children=[
            dmc.Divider(label="Map", labelPosition="center", size="xs"),
            dmc.Space(h=20),
            dmc.Grid(
                list(map(
                    lambda x: dmc.Col(minimap_button(id_prefix, x, MAP_TYPES[0]), style={"textAlign": "center"}, span=3),
                    MAPS)
                ),
                gutter="sm",
                grow=True,
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Overlay", labelPosition="center", size="xs"),
            dmc.Space(h=20),
            dmc.Grid(
                list(map(
                    lambda x: dmc.Col(minimap_button(id_prefix, x, MAP_TYPES[1]), style={"textAlign": "center"}, span=3),
                    OVERLAYS)
                ),
                gutter="sm",
                grow=True,
            ),
        ],
    )


def minimap_button(id_prefix, map_config, role):
    return html.Div(dmc.Stack(
        children=[
            html.Div(
                dmc.Image(
                    src=map_config.image,
                    alt="map",
                    width=48,
                    height=48,
                    radius=5,
                ),
                className="map-image-selected" if map_config.index == 0 else ""
            ),
            dmc.Text(
                size="xs",
                children=map_config.title,
            )
        ],
        align="center",
        spacing="xs",
    ),
        id={'role': role, 'index': map_config.index, 'place': id_prefix},
    )


def update_store(store, collection):
    index_map = store["index"]
    new_map = next(x for x in collection if x.index == index_map)
    if new_map is None:
        return dash.no_update
    return new_map.source, new_map.source_attribution


@app.callback(
    Output(ID_BASE_LAYER_MAP, "url"),
    Output(ID_BASE_LAYER_MAP, "attribution"),
    Input(ID_BASE_MAP_STORE, "data")
)
def handle_map_store_update(store):
    return update_store(store, MAPS)


@app.callback(
    Output(ID_OVERLAY_MAP, "url"),
    Output(ID_OVERLAY_MAP, "attribution"),
    Input(ID_OVERLAY_MAP_STORE, "data")
)
def handle_overlay_store_update(store):
    return update_store(store, OVERLAYS)


def handle_map_update(_):
    if dash.ctx.triggered_id is None:
        return dash.no_update
    return {"index": dash.ctx.triggered_id["index"]}


@app.callback(
    Output(ID_BASE_MAP_STORE, "data"),
    Input({'role': MAP_TYPES[0], 'index': ALL, 'place': ALL}, 'n_clicks'),
)
def handle_map_update(_):
    if dash.ctx.triggered_id is None:
        return dash.no_update
    return {"index": dash.ctx.triggered_id["index"]}


@app.callback(
    Output(ID_OVERLAY_MAP_STORE, "data"),
    Input({'role': MAP_TYPES[1], 'index': ALL, 'place': ALL}, 'n_clicks'),
)
def handle_map_update(_):
    if dash.ctx.triggered_id is None:
        return dash.no_update
    return {"index": dash.ctx.triggered_id["index"]}


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
