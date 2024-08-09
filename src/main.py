from dash import Dash
import dash_bootstrap_components as dbc
import datetime
import dash

import diskcache
from dash.long_callback import DiskcacheLongCallbackManager

cache = diskcache.Cache("./cache")

    #dbc.themes.BOOTSTRAP,
external_stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]

dash._dash_renderer._set_react_version('18.2.0')

app = Dash(
    __name__,
    title="Mitwelten Discover",
    external_stylesheets=external_stylesheets,
    external_scripts=[{'src':'assets/util.js','type':'module'}],
    suppress_callback_exceptions=True,
    requests_pathname_prefix="/app/",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    use_pages=True,
    pages_folder="",
)


app.enable_dev_tools(
    dev_tools_ui=True,
    dev_tools_serve_dev_bundles=True,
    dev_tools_hot_reload=True
)
