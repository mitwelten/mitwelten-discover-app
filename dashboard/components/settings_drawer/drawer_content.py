import dash_mantine_components as dmc
from dash import html

from dashboard.components.settings_drawer.components.date_time_section import date_time_section
from dashboard.components.settings_drawer.components.general_controls import general_controls
from dashboard.components.settings_drawer.components.source_filter import source_filter
from dashboard.components.settings_drawer.components.tag_filter import tag_filter
from dashboard.config.id_config import *


def divider(title: str):
    return dmc.Divider(label=title, labelPosition="center", size="md")


drawer_content = dmc.Container(
    children=[
        dmc.Title("Mitwelten Discover", align="center", order=1),
        dmc.Space(h=30),
        dmc.ScrollArea([
            divider("Date Range"),
            date_time_section(),
            divider("Data Source"),
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
            style={"height": "100%", "paddingLeft": "5px"}
        )],
    fluid=True,
    style={"height": "calc(100vh - 100px)", "paddingRight": "0px"}
)
