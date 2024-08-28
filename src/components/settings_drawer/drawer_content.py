import dash_mantine_components as dmc

from src.config.app_config import DISCOVER_DESCRIPTION, PRIMARY_COLOR
from src.components.settings_drawer.components.date_time_section import date_time_section
from src.components.settings_drawer.components.general_controls import general_controls
from src.components.settings_drawer.components.source_filter import source_filter
from src.components.settings_drawer.components.tag_filter import tag_filter
from src.config.id_config import *
from src.config.app_config import SETTINGS_DRAWER_WIDTH
from dash_iconify import DashIconify


def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md", mt=5)

label = dmc.Stack(
        children=[dmc.Title(
            "Mitwelten Discover is a map-based publication of the research project MITWELTEN.", order=3), 
                  dmc.Text(DISCOVER_DESCRIPTION)
                  ]
        )
title = dmc.Center(
        dmc.Tooltip(
            multiline=True,
            label=label,
            position="right",
            openDelay=500,
            w=350,
            m=10,
            p=20,
            color=PRIMARY_COLOR,
            children= dmc.Title(
                "Mitwelten Discover", 
                order=3, 
                style={"cursor": "pointer"}
                )
            )
        )

def drawer_content(args): 
    return dmc.Container(
            children=[
                dmc.ScrollArea(
                dmc.Flex([
                    dmc.Stack(
                        gap="xs",
                        children=[
                        title,
                        divider("Time Frame"),
                        date_time_section(args),
                        divider("Data Sets"),
                        source_filter(args),
                        divider("Tags"),
                        tag_filter(args),
                        dmc.Space(h=10),
                        general_controls(args),
                        ]),
                ], 
                         justify="space-between", 
                         direction="column",
                         style={"height":"100%"}
                         )),
                ], style={"height":"100%"},
                )
