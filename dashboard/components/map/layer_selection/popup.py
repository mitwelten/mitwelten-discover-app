import dash_mantine_components as dmc
from dash import html

from dashboard.components.button.components.action_button import action_button
from dashboard.config.map import MAPS, OVERLAYS, MAP_TYPES


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
