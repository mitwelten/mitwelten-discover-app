import dash_mantine_components as dmc

from src.config.app_config import DISCOVER_DESCRIPTION
from src.components.settings_drawer.components.date_time_section import date_time_section
from src.components.settings_drawer.components.general_controls import general_controls
from src.components.settings_drawer.components.source_filter import source_filter
from src.components.settings_drawer.components.tag_filter import tag_filter
from src.config.id_config import *


def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md")


def drawer_content(args): 
    return dmc.Container(
            children=[
                dmc.Center(
                    dmc.HoverCard(
                        position="top",
                        withArrow=True,
                        width="500px",
                        shadow="lg",
                        style={"display": "flex", "alignItems":"center"},
                        children=[
                            dmc.HoverCardTarget(
                                children=[
                                    dmc.Title(
                                        "Mitwelten Discover", 
                                        align="center", 
                                        order=1, 
                                        style={"cursor": "pointer"}
                                        ),
                                    ],
                                ),
                            dmc.HoverCardDropdown(
                                children=[
                                    dmc.Text( DISCOVER_DESCRIPTION, size="sm"),
                                    dmc.Space(h=10),
                                    dmc.Group([
                                        dmc.Text("For more information visit:", size="sm"),
                                        dmc.Anchor("mitwelten.org", href="https://mitwelten.org", target="_blank", size="sm"),
                                        ], spacing="xs"),
                                    ],
                                style={"padding": "30px"}
                                )
                            ],
                        ),
                    ),
                dmc.Space(h=30),
                dmc.ScrollArea([
                    divider("Time Frame"),
                    date_time_section(args),
                    divider("Data Sets"),
                    source_filter(args),
                    divider("Tags"),
                    tag_filter(args),
                    divider("Settings"),
                    general_controls(args),
                    dmc.Group([
                        dmc.Text("Found a bug?", size="sm"),
                        dmc.Anchor(
                            "Submit an issue",
                            href="https://github.com/mitwelten/mitwelten-discover-app/issues",
                            target="_blank",
                            size="sm"
                            ),
                        ])
                    ],
                               offsetScrollbars=True,
                               type="scroll",
                               style={"height": "100%"}
                               )],
                #fluid=True,
                style={"height": "calc(100vh - 100px)", "paddingRight": "0px", "paddingLeft": "0px"}
                )
