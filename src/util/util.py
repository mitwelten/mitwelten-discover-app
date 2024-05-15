import time
import re
import pytz
from datetime import datetime
from dash import html
from urllib import parse 


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

def get_param_if_present(param, data):

    if data.get(param) is not None and data[param]:
        if isinstance(data[param], list):
            return f"{param}={','.join(data[param])}"
        else:
            return f"{param}={data[param]}"
    return None


def query_data_to_string(data):
    params : list[str] = []
    for key in ["start", "end", "timerange", "fs", "lat", "lon", "zoom", "tags", "devices", "id"]:
        param = get_param_if_present(key, data)
        if param is not None and param != "":
            params.append(param)
    return "?" + "&".join(params)


def query_string_to_dict(query:str):
    if len(query) > 0 and query[0] == "?":
        query = query[1:] # remove the question mark
    params = parse.parse_qs(query)
    return {k: v[0] for k,v in params.items()}


def update_query_data(data, params: dict):
    # update data dict with params
    for param in params.keys():
        if params[param] is not None:
            data[param] = params[param]
        else:
            if data.get(param) is not None:
                del data[param]

    return dict(sorted(data.items()))

