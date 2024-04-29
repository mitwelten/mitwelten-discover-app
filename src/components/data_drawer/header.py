
import dash_mantine_components as dmc

from src.config.id_config import *
from src.config.app_config import PRIMARY_COLOR
from dash_iconify import DashIconify

def bottom_drawer_content(title, desc, tags, icon, theme, title_icons=None, test_icons = False):


    info_text = dmc.HoverCard(
            position="top",
            withArrow=True,
            width="200px",
            shadow="md",
            style={"display": "flex", "align-items":"center"},
            children=[
                dmc.HoverCardTarget(
                    children=dmc.ThemeIcon(
                        size="sm",
                        color=PRIMARY_COLOR,
                        variant="light",
                        children=DashIconify(icon="material-symbols:help", width=25),
                        ),
                    ),
                dmc.HoverCardDropdown(children=dmc.Text(desc, size="sm"))
                ],
            )

    return dmc.Container([
        dmc.Grid([
            dmc.Col(
                children=[
                dmc.Stack(
                    style={"width":"90%"},
                    spacing="xs",
                    children=[
                        dmc.Group(
                            spacing="xs",
                            align="center",
                            children=[
                                dmc.Title(title),
                                info_text if desc != "" else None,
                                title_icons
                            ], 
                        ),
                        dmc.Grid(
                            children=[
                                dmc.Col(children=[
                                    dmc.ScrollArea(
                                        children=[
                                            dmc.ChipGroup(
                                                [dmc.Chip(tag, size="xs", color=PRIMARY_COLOR) for tag in tags],
                                                noWrap=True
                                            )
                                        ],
                                        type="hover",
                                        offsetScrollbars=True
                                    ),

                                ],span=12),

                                #dmc.Col(children=[
                                #    dmc.Text(f" {date_from} - {date_to}", align="end", color="dimmed", size="sm"), 
                                #],span=12, sm=5),
                            ]
                        ),
                    ])
            ],
                span=9,
                sm=10
            ),
            dmc.Col(
                children=dmc.Image(
                    src=f"assets/markers/test/{icon}" if test_icons else f"assets/markers/{icon}",
                    alt="note icon", 
                    style={"min-width": "25px", "width": "50px"}
                ),
                span=3,
                sm=2,
                style={"display":"flex", "justify-content":"flex-end"}
            )
        ]), 
        dmc.Space(h=10),
        dmc.Divider(size="xs"),
    ], fluid=True
                         )
