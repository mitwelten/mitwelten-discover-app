import dash_mantine_components as dmc
from dash import html

from src.components.button.components.action_button import action_button
from src.config.map_config import MAPS, OVERLAYS, MAP_TYPES


def map_menu_popup(id_prefix):
    menu_entries = []
    menu_entries.append(dmc.MenuLabel("Map"))

    for map_config in MAPS:
        menu_entries.append(
                dmc.MenuItem(
                    map_config.title,
                    leftSection=html.Div(
                        dmc.Image(src=map_config.image, alt="map", w=48, h=48, radius=5),
                        className="map-image-selected" if map_config.index == 0 else ""
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
                    leftSection=html.Div(
                        dmc.Image(src=overlay_config.image, alt="map", w=48, h=48, radius=5),
                        className="map-image-selected" if overlay_config.index == 0 else ""
                        ),
                    id={'role': MAP_TYPES[1], 'index': overlay_config.index, 'place': id_prefix},
                    )
                )

    return dmc.Container(
            dmc.Menu([
                    dmc.MenuTarget(action_button(icon="material-symbols:layers-outline")),
                    dmc.MenuDropdown(menu_entries),
                    ],
                trigger="hover",
                classNames="map-menu",
                transitionProps={"transition": "scale-y", "duration": 100},
                position="bottom-end",
                withArrow=True,
                arrowSize=10,
                arrowOffset=15,
                zIndex=500000,
                ),
            visibleFrom="sm",
            )
