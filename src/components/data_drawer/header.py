import dash_mantine_components as dmc

from src.config.app_config import PRIMARY_COLOR
from src.config.id_config import *

def data_drawer_header(title, tags, icon, theme, title_icons=None, info=None):
    return dmc.Container([
        dmc.Grid([
            dmc.GridCol(
                children=[
                dmc.Stack(
                    style={"width":"90%"},
                    gap="xs",
                    children=[
                        dmc.Group(
                            gap="xs",
                            align="center",
                            children=[
                                dmc.Title(title, order=4),
                                title_icons
                                ], 
                            ),
                        dmc.ScrollArea(
                            w="100%",
                            h=35,
                            type="hover",
                            offsetScrollbars=True,
                            children=[
                                dmc.Group(
                                    gap="xs",
                                    wrap=False,
                                    children=[
                                        dmc.Text(info, size="xs", c="dimmed") if info else None,
                                        dmc.Group([dmc.Badge(tag, size="md", color=PRIMARY_COLOR) for tag in tags])
                                        ]),
                                ],
                            ),
                        ])
            ],
                span=10,
                ),
            dmc.GridCol(
                dmc.Image(
                    src=icon,
                    w=50,
                    h=50,
                    visibleFrom="xs",
                    ),
                span=2,
                #sm=2,
                style={"display":"flex", "justifyContent":"flex-end"}
                )
        ]), 
        dmc.Space(h=10),
        dmc.Divider(size="xs"),
    ], fluid=True
                         )
