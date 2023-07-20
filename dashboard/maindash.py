from dash import Dash
import dash_bootstrap_components as dbc

external_stylesheets = [
    open("./dashboard/assets/styles/background_map_styles.css"),
    open("./dashboard/assets/styles/component_styles.css"),
    dbc.themes.BOOTSTRAP,
]

app = Dash(
    __name__,
    title="Mitwelten Discover",
    external_stylesheets=external_stylesheets,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
