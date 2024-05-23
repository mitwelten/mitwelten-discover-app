
import dash_mantine_components as dmc

from src.config.id_config import *
from src.config.app_config import PRIMARY_COLOR
from dash_iconify import DashIconify

def bottom_drawer_content(title, tags, icon, theme, title_icons=None):
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
                    src=f"assets/markers/{icon}",
                    alt="note icon", 
                    style={"minWidth": "25px", "width": "50px"}
                ),
                span=3,
                sm=2,
                style={"display":"flex", "justifyContent":"flex-end"}
            )
        ]), 
        dmc.Space(h=10),
        dmc.Divider(size="xs"),
    ], fluid=True
                         )
