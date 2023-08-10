import dash_mantine_components as dmc
from dashboard.config.id import *

from dashboard.components.map.layer_selection.drawer import map_menu_drawer
from dashboard.components.map.layer_selection.popup import map_menu_popup


def map_layer_menus():
    return [
        dmc.MediaQuery(
            map_menu_popup("menu"),
            smallerThan="sm",
            styles={"visibility": "hidden"}
        ),

        dmc.Drawer(
            map_menu_drawer("drawer"),
            id=ID_MAP_LAYER_BOTTOM_DRAWER,
            size="lg",
            zIndex=90000,
        )
    ]
