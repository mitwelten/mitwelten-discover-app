import dash_mantine_components as dmc
from dash import html

from src.components.settings_drawer.components.date_time_section import date_time_section
from src.components.settings_drawer.components.general_controls import general_controls
from src.components.settings_drawer.components.source_filter import source_filter
from src.components.settings_drawer.components.tag_filter import tag_filter
from src.config.id_config import *


def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md")


drawer_content = dmc.Container(
    children=[
        dmc.Title("Mitwelten Discover", align="center", order=1),
        dmc.Space(h=30),
        dmc.ScrollArea([
            divider("Time Frame"),
            date_time_section(),
            divider("Data Sets"),
            source_filter(),
            divider("Tags"),
            tag_filter(),
            divider("Settings"),
            general_controls(),
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
