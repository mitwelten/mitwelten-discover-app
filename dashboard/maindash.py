from dash import Dash
import dash_bootstrap_components as dbc

import diskcache
from dash.long_callback import DiskcacheLongCallbackManager

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

external_stylesheets = [
    open("./dashboard/assets/styles/map_styles.css"),
    open("./dashboard/assets/styles/component_styles.css"),
    dbc.themes.BOOTSTRAP,
]

app = Dash(
    __name__,
    title="Mitwelten Discover",
    external_stylesheets=external_stylesheets,
    long_callback_manager=long_callback_manager,
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
