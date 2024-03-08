import time
import pytz
from datetime import datetime
from dash import html


def local_formatted_date(date: str, date_format="%d %b %Y • %H:%M"):
    tz = pytz.timezone(time.tzname[0])
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
