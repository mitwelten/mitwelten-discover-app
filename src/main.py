from dash import Dash
import dash_bootstrap_components as dbc

import diskcache
from dash.long_callback import DiskcacheLongCallbackManager

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
]

app = Dash(
    __name__,
    title="Mitwelten Discover",
    external_stylesheets=external_stylesheets,
    external_scripts=[{'src':'assets/util.js','type':'module'}],
    long_callback_manager=long_callback_manager,
    suppress_callback_exceptions=True,
    requests_pathname_prefix="/app/",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.enable_dev_tools(
    dev_tools_ui=True,
    dev_tools_serve_dev_bundles=True,
    dev_tools_hot_reload=True
)
