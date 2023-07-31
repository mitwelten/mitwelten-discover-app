import dash
import dash_mantine_components as dmc
from dash import html, Output, Input, ALL, callback

from dashboard.components.action_button import action_button
from dashboard.config.id_config import *
from dashboard.config.map_config import MAPS
from dashboard.maindash import app

MAP_TYPE = [
    dict(
        id=ID_TILE_LAYER_MAP,
        store=ID_BASE_MAP_STORE,
        name="base",
        data=list(filter(lambda m: not m.overlay, MAPS))
    ),
    dict(
        id=ID_OVERLAY_MAP,
        store=ID_OVERLAY_MAP_STORE,
        name="overlay",
        data=list(filter(lambda m: m.overlay, MAPS))
    )
]


def map_menu_popup(id_prefix):
    menu_entries = [dmc.MenuLabel("Map")]

    for map_config in MAP_TYPE[0]["data"]:
        menu_entries.append(
            dmc.MenuItem(
                map_config.title,
                icon=html.Div(dmc.Image(src=map_config.image, alt="map", width=48, radius=5)),
                id={'role': "base", 'index': map_config.id, 'place': id_prefix},
            )
        )
    menu_entries.append(dmc.MenuDivider())
    menu_entries.append(dmc.MenuLabel("Overlays"))

    for map_config in MAP_TYPE[1]["data"]:
        menu_entries.append(
            dmc.MenuItem(
                map_config.title,
                icon=html.Div(dmc.Image(src=map_config.image, alt="map", width=48, radius=5)),
                id={'role': "overlay", 'index': map_config.id, 'place': id_prefix},
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


def map_selection(id_prefix):
    return dmc.Container(
        children=[
            dmc.Grid(
                list(map(
                    lambda x: dmc.Col(minimap_button(id_prefix, x), style={"textAlign": "center"}, span=3),
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
                    lambda x: dmc.Col(minimap_button(f"test-{id_prefix}", x), style={"textAlign": "center"}, span=3),
                    MAPS[1:-1])
                ),
                gutter="xl",
                grow=True,
            ),
        ],
    )


def minimap_button(id_prefix, map_config):
    return html.Div(
        id={'role': "minimap-btn", 'index': map_config.id, 'place': id_prefix},
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
    ),


def handle_store_update(store):
    id_map = store["id"]
    return MAPS[id_map].source, MAPS[id_map].source_attribution


for map_type in MAP_TYPE:
    callback(
        Output(map_type["id"], "url"),
        Output(map_type["id"], "attribution"),
        Input(map_type["store"], "data")
    )(handle_store_update)


def handle_map_update(_):
    if dash.ctx.triggered_id is None:
        return dash.no_update
    return {"id": dash.ctx.triggered_id["index"]}


for map_type in MAP_TYPE:
    callback(
        Output(map_type["store"], "data"),
        Input({'role': map_type["name"], 'index': ALL, 'place': ALL}, 'n_clicks'),
    )(handle_map_update)


@app.callback(
        Output({'role': "overlay", 'index': ALL, 'place': "menu"}, 'icon'),
        Input({'role':  "overlay", 'index': ALL, 'place': "menu"}, 'n_clicks'),
        Input({'role':  "overlay", 'index': ALL, 'place': "menu"}, 'icon'),
        prevent_initial_call=True
)
def update_map_icon(_, icons):
    # Note: ID's of tile and overlay layers are contiguous
    offset = (len(MAP_TYPE[0]["data"]) - 1)

    overlay_id = dash.ctx.triggered_id["index"]
    clicked_item_id = overlay_id - offset

    for icon in icons:
        icon["props"]["className"] = ""

    icons[clicked_item_id-1]["props"]["className"] = "map-image-selected"
    return icons


@app.callback(
    Output({'role': "base", 'index': ALL, 'place': "menu"}, 'icon'),
    Input({'role':  "base", 'index': ALL, 'place': "menu"}, 'n_clicks'),
    Input({'role':  "base", 'index': ALL, 'place': "menu"}, 'icon'),
)
def update_map_icon(_, icons):
    base_id = dash.ctx.triggered_id["index"] if dash.ctx.triggered_id is not None else 0
    for icon in icons:
        icon["props"]["className"] = ""

    icons[base_id]["props"]["className"] = "map-image-selected"
    return icons
