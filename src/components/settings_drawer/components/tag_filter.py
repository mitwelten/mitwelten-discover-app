import re

import dash_mantine_components as dmc
from dash import Input, Output, State

from src.model.url_parameter import UrlParameter
from src.data.init import init_tags
from src.config.id_config import *
from src.main import app
from src.url.parse import update_query_data

fs_desc = dmc.Stack([
    dmc.Text("Field Study 1: Merian Gärten",   size="sm"),
    dmc.Text("Field Study 2: Dreispitz",       size="sm"),
    dmc.Text("Field Study 3: Reinacher Heide", size="sm"),
], gap="sm")


def tag_filter(params: UrlParameter, all_tags):
    all_tags = [tag["name"] for tag in all_tags]

    predicate = re.compile("FS\d")

    fs_tags = []
    for tag in all_tags:
        if predicate.match(tag):
            fs_tags.append(tag)
    fs_tags = list(sorted(fs_tags))

    tags = sorted([t for t in all_tags if t not in fs_tags])
    tags_value = params.tags if params.tags is not None else []

    return dmc.TagsInput(
            id=ID_TAGS,
            clearable=False,
            value=tags_value,
            placeholder="Pick tag from list",
            data=[
                {"group": "Field Study", "items": fs_tags},
                {"group": "Additional", "items": tags},
                ],
            )



@app.callback(
    Output(ID_QUERY_PARAM_STORE, "data", allow_duplicate=True),
    Input(ID_TAGS, "value"),
    State(ID_QUERY_PARAM_STORE, "data"),
    prevent_initial_call=True,
)
def update_fs_tag_in_url_params(value, data):
    value = "+".join(value)
    value = value.replace(" ", "_")
    return update_query_data(data, {"tags": value})

