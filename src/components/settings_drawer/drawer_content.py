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
    return dmc.Divider(label=title, labelPosition="center", size="md", mt=10)


title = dmc.Center(
                    #dmc.HoverCard(
                    #    position="top",
                    #    withArrow=True,
                    #    width="500px",
                    #    shadow="lg",
                    #    zIndex=999999,
                    #    styles={"display": "flex", "alignItems":"center"},
                    #    children=[
                    #        dmc.HoverCardTarget(
                    #            children=[
                    #                dmc.Center(
                    #                dmc.Title(
                    #                    "Mitwelten Discover", 
                    #                    order=3, 
                    #                    style={"cursor": "pointer"}
                    #                    )
                    #                ),
                    #                ],
                    #            ),
                    #        dmc.HoverCardDropdown(
                    #            children=[
                    #                dmc.Text( DISCOVER_DESCRIPTION, size="sm"),
                    #                dmc.Space(h=10),
                    #                dmc.Group([
                    #                    dmc.Text("For more information visit:", size="sm"),
                    #                    dmc.Anchor("mitwelten.org", href="https://mitwelten.org", target="_blank", size="sm"),
                    #                    ], gap="xs"),
                    #                ],
                    #            style={"padding": "30px"}
                    #            )
                    #        ],
                    #    ),

                    dmc.Tooltip(
                        multiline=True,
                        label=DISCOVER_DESCRIPTION,
                        position="right",
                        openDelay=500,
                        w=350,
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
                dmc.Flex([
                    dmc.Stack([
                        title,
                        dmc.Space(h=10),
                        divider("Time Frame"),
                        date_time_section(args),
                        divider("Data Sets"),
                        source_filter(args),
                        divider("Tags"),
                        tag_filter(args),
                        ], gap="md"),
                    general_controls(args),
                ], 
                         justify="space-between", 
                         direction="column",
                         style={"height":"100%"}
                         ),
                ], style={"height":"100%"},
                    #style={"height": "calc(100vh - 100px)", "paddingRight": "0px", "paddingLeft": "0px"}
                )
