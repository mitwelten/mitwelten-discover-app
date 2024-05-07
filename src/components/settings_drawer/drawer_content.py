import dash_mantine_components as dmc
from dash import html

from src.config.app_config import DISCOVER_DESCRIPTION, PRIMARY_COLOR
from src.components.settings_drawer.components.date_time_section import date_time_section
from src.components.settings_drawer.components.general_controls import general_controls
from src.components.settings_drawer.components.source_filter import source_filter
from src.components.settings_drawer.components.tag_filter import tag_filter
from src.config.id_config import *

from dash_iconify import DashIconify

def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md")


def drawer_content(args): 
    return dmc.Container(
            children=[
                dmc.Group([
                    dmc.Title("Mitwelten Discover", align="center", order=1),
                    dmc.HoverCard(
                        position="top",
                        withArrow=True,
                        width="500px",
                        shadow="lg",
                        style={"display": "flex", "alignItems":"center"},
                        children=[
                            dmc.HoverCardTarget(
                                children=dmc.ThemeIcon(
                                    size="sm",
                                    variant="filled",
                                    radius="sm",
                                    color=PRIMARY_COLOR,
                                    children=DashIconify(icon="material-symbols:info-i-rounded", width=16)
                                    ),
                                ),
                            dmc.HoverCardDropdown(children=DISCOVER_DESCRIPTION)
                            ],
                        ),
                    ]),
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
