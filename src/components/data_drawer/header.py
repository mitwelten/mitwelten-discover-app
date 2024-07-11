import dash_mantine_components as dmc

from src.config.id_config import *

def bottom_drawer_content(title, tags, icon, theme, title_icons=None, info=None):
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
                                dmc.Title(title),
                                title_icons
                                ], 
                            ),
                        dmc.ScrollArea(
                            children=[
                                dmc.Group([
                                dmc.Text(info, size="sm", c="dimmed") if info else None,
                                #dmc.ChipGroup(
                                #    [dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in tags],
                                #    noWrap=True
                                #    )
                                ]),
                                ],
                            type="hover",
                            offsetScrollbars=True
                            ),
                        ])
            ],
                span=10,
                ),
            dmc.GridCol(
                dmc.Image(
                    src=f"assets/markers/{icon}",
                    alt="note icon", 
                    w=50,
                    h=50,
                    visibleFrom="xs",
                    #style={"minWidth": "25px", "width": "25px"}
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
