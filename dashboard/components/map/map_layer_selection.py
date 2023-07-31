import dash
import dash_mantine_components as dmc
from dash import html, Output, Input, ALL, callback, State

from dashboard.components.action_button import action_button
from dashboard.config.id_config import *
from dashboard.config.map_config import MAPS, OVERLAYS
from dashboard.maindash import app


MAP_TYPES = ["base", "overlay"]


def map_menu_popup(id_prefix):
    menu_entries = [dmc.MenuLabel("Map")]

    for map_config in MAPS:
        menu_entries.append(
            dmc.MenuItem(
                map_config.title,
                icon=html.Div(dmc.Image(src=map_config.image, alt="map", width=48, radius=5)),
                id={'role': "base", 'index': map_config.index, 'place': id_prefix},
            )
        )
    menu_entries.append(dmc.MenuDivider())
    menu_entries.append(dmc.MenuLabel("Overlays"))

    for overlay_config in OVERLAYS:
        menu_entries.append(
            dmc.MenuItem(
                overlay_config.title,
                icon=html.Div(dmc.Image(src=overlay_config.image, alt="map", width=48, radius=5)),
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
    )


def map_menu_drawer(id_prefix):
    return dmc.Container(
        children=[
            dmc.Grid(
                list(map(
                    lambda x: dmc.Col(minimap_button(id_prefix, x, MAP_TYPES[0]), style={"textAlign": "center"}, span=3),
                    MAPS)
                ),
                gutter="xl",
                grow=True,
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Overlays", labelPosition="center", size="sm"),
            dmc.Space(h=20),
            dmc.Grid(
                list(map(
                    lambda x: dmc.Col(minimap_button(id_prefix, x, MAP_TYPES[1]), style={"textAlign": "center"}, span=3),
                    OVERLAYS)
                ),
                gutter="xl",
                grow=True,
            ),
        ],
    )


def minimap_button(id_prefix, map_config, role):
    return html.Div(
        id={'role': role, 'index': map_config.index, 'place': id_prefix},
        className="minimap-btn",
        children=[
            html.Div(
                className="minimap-button-container",
                children=[
                    html.Div(
                        className="map-image",
                        children=[
                            dmc.Image(
                                src=map_config.image,
                                alt="map",
                                width=48,
                                radius=5,
                            ),
                        ]
                    ),
                    html.P(
                        className="minimap-button-label",
                        children=map_config.title,
                        style={'fontSize': 10}
                    )
                ]
            ),
        ]
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


app.callback(
    Output(ID_BASE_MAP_STORE, "data"),
    Input({'role': MAP_TYPES[0], 'index': ALL, 'place': ALL}, 'n_clicks'),
)(handle_map_update)


app.callback(
    Output(ID_OVERLAY_MAP_STORE, "data"),
    Input({'role': MAP_TYPES[1], 'index': ALL, 'place': ALL}, 'n_clicks'),
)(handle_map_update)


def update_map_icon(_, icons):
    overlay_id = dash.ctx.triggered_id["index"]

    for icon in icons:
        icon["props"]["className"] = ""

    icons[overlay_id]["props"]["className"] = "map-image-selected"
    return icons


for map_type in MAP_TYPES:
    app.callback(
            Output({'role': map_type, 'index': ALL, 'place': "menu"}, 'icon'),
            Input({'role':  map_type, 'index': ALL, 'place': "menu"}, 'n_clicks'),
            State({'role':  map_type, 'index': ALL, 'place': "menu"}, 'icon'),
            prevent_initial_call=True
    )(update_map_icon)

