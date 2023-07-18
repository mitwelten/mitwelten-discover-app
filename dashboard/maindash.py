from dash import Dash

external_stylesheets = [open("./dashboard/assets/styles/background_map_styles.css")]

app = Dash(
    __name__,
    title="Mitwelten Discover",
    external_stylesheets=external_stylesheets,
)
