import dash_mantine_components as dmc

from src.model.url_parameter import UrlParameter
from src.config.app_config import DISCOVER_DESCRIPTION, PRIMARY_COLOR
from src.components.settings_drawer.components.date_time_section import date_time_section
from src.components.settings_drawer.components.general_controls import general_controls
from src.components.settings_drawer.components.source_filter import source_filter
from src.components.settings_drawer.components.tag_filter import tag_filter
from src.components.settings_drawer.components.device_filter import device_filter
from src.config.id_config import *


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

def drawer_content(params: UrlParameter, all_tags, active_device): 
    return dmc.Container(
            children=[
                dmc.ScrollArea(
                dmc.Flex([
                    dmc.Stack(
                        gap="xs",
                        children=[
                        title,
                        divider("Time Frame"),
                        date_time_section(params),
                        divider("Data Sets"),
                        source_filter(params),
                        divider("Tags"),
                        tag_filter(params, all_tags),
                        divider("Node ID"),
                        device_filter(active_device),
                        dmc.Space(h=10),
                        general_controls(),
                        ]),
                ], 
                         justify="space-between", 
                         direction="column",
                         style={"height":"100%"}
                         )),
                ], style={"height":"100%"},
                )
