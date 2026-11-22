from dash import Dash
import dash

import diskcache

cache = diskcache.Cache("./cache")


dash._dash_renderer._set_react_version('19.2.4')  # DMC 3 requires React 19

app = Dash(
    __name__,
    title="Mitwelten Discover",
    external_scripts=[{'src':'assets/util.js','type':'module'}],
    suppress_callback_exceptions=True,
    requests_pathname_prefix="/app/",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    use_pages=True,
    pages_folder="",
)


# app.enable_dev_tools(
#     dev_tools_ui=True,
#     dev_tools_serve_dev_bundles=True,
#     dev_tools_hot_reload=True
# )
