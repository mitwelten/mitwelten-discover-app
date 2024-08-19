import re
import pytz
from datetime import datetime
from dash import html
import dash_mantine_components as dmc
from src.config.app_config import CHART_DRAWER_HEIGHT

def local_formatted_date(date: str, timezone=None, date_format="%d %b %Y • %H:%M"):
    if timezone == "" or timezone is None:
        timezone = "Europe/Zurich"
    tz = pytz.timezone(timezone)
    dt = datetime.fromisoformat(date)
    local_dt = dt.astimezone(tz)
    return datetime.strftime(local_dt, date_format)


def get_identification_label(source) -> str:
    if source.get('node_label') is not None:
        return source.get('node_label')

    if source.get('node') is not None:
        if source.get("node").get("node_label") is not None:
            node_label = source['node']['node_label']
        else:
            node_label = source['node']
    else:
        node_label = source.get("id")

    return node_label


def apply_newlines(text: str):
    children = []
    if text is not None:
        text_list = text.split("\n")
        for para in text_list:
            children.append(para)
            children.append(html.Br())
    return children


def text_to_html_list(text: str):
    elems = text_to_dash_elements(text)
    return html.Div(
            children=[
                dmc.Spoiler(
                    children=dmc.Text(elems),
                    showLabel="Show more",
                    hideLabel="Hide",
                    maxHeight=200,
                    hiddenFrom="sm"
                    ),
                dmc.Text(
                    children=elems,
                    visibleFrom="sm"
                    )
                ]
                )


def text_to_dash_elements(text):
    elements = []
    if text is None or text == "":
        return []
    lines = text.split('\n')

    url_pattern = re.compile(
        r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))" 
    )

    for line in lines:
        parts = []
        start = 0

        for match in url_pattern.finditer(line):
            url = match.group(1)
            parts.append(line[start:match.start()])
            href = url if url.startswith('http') else 'http://' + url
            parts.append(html.A(href=href, children=[url], target="_blank"))
            start = match.end()

        parts.append(line[start:])

        for part in parts:
            if isinstance(part, str) and part:
                elements.append(part)
            elif part:
                elements.append(part)
        if line != lines[-1]:
            elements.append(html.Br())

    return elements

