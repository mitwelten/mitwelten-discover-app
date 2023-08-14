import dash
import dash_mantine_components as dmc
from dash import Output, Input, html, ALL, State

from dashboard.components.notifications.notification import create_notification, NotificationType
from dashboard.config.app import SETTINGS_DRAWER_WIDTH
from dashboard.config.chart import get_supported_chart_types
from dashboard.config.id import *
from dashboard.maindash import app
from util.functions import safe_reduce, ensure_marker_visibility


def chart_drawer():
    return dmc.Drawer(
        opened=False,
        id=ID_CHART_DRAWER,
        zIndex=20000,
        size="50%",
        closeOnClickOutside=False,
        closeOnEscape=False,
        withOverlay=False,
        className="chart-drawer",
        children=[
            dmc.LoadingOverlay(
                html.Div(id=ID_CHART_CONTAINER, className="measurement-chart", style={"margin": "20px"}),
                loaderProps={"variant": "dots", "color": "mitwelten_pink", "size": "xl"},
            )
        ],
    )


@app.callback(
    Output(ID_MAP_CONTAINER, "style"),
    Output(ID_CHART_DRAWER, "styles"),
    Input(ID_SETTINGS_DRAWER, "opened")
)
def settings_drawer_state(state):
    width_reduced = {"width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}
    full_width = {"width": "100vw"}
    if state:
        return width_reduced, {"drawer": {"left": "400px", "width": f"calc(100vw - {SETTINGS_DRAWER_WIDTH}px"}}
    return full_width, {"drawer": {"left": "0", "width": "100vw"}}

# idee => separates callback mit pattern matching und ein store, der die seleben id's hat, damit man den getriggerten marker herausfinden kann

@app.callback(
    Output(ID_CHART_DRAWER, "opened"),
    Output(ID_CHART_DRAWER, "position"),
    Output(ID_MARKER_CLICK_STORE, "data"),
    Output(ID_CURRENT_CHART_DATA_STORE, "data"),
    Output(ID_NOTIFICATION_CONTAINER, "children", allow_duplicate=True),
    Output(ID_MAP, "center", allow_duplicate=True),
    Input({"role": ALL, "id": ALL, "label": ALL, "lat": ALL, "lon": ALL}, "n_clicks"),
    State(ID_MARKER_CLICK_STORE, "data"),
    State(ID_CURRENT_CHART_DATA_STORE, "data"),
    State(ID_MAP, "bounds"),
    State(ID_MAP, "center"),
    prevent_initial_call=True,
)
def marker_click(n_clicks, data, chart_data, bounds, map_center):
    print(dash.ctx.triggered_id)
    # determine whether the callback is triggered by a click
    # necessary, because adding markers to the map triggers the callback
    click_sum = safe_reduce(lambda x, y: x + y, n_clicks)
    has_click_triggered = False

    if click_sum is not None:
        has_click_triggered = click_sum != data["clicks"]
        data["clicks"] = click_sum

    open_drawer = False
    notification = None
    if has_click_triggered and dash.ctx.triggered_id is not None:
        trigger_id = dash.ctx.triggered_id
        if trigger_id["role"] not in get_supported_chart_types().keys():
            notification = create_notification(
                trigger_id["role"],
                "No further data available!",
                NotificationType.INFO
            )
        else:
            map_center = ensure_marker_visibility(map_center, bounds, trigger_id)
            chart_data = dict(
                role=trigger_id["role"],
                id=trigger_id["id"],
                lat=trigger_id["lat"],
                lon=trigger_id["lon"]
            )
            open_drawer = True

    return open_drawer, "bottom", data, chart_data, notification, map_center


@app.callback(
    Output(ID_CHART_CONTAINER, "children"),
    Input(ID_CURRENT_CHART_DATA_STORE, "data"),
    State(ID_APP_THEME, "theme"),
    State(ID_ENVIRONMENT_LEGEND_STORE, "data"),
    prevent_initial_call=True
)
def display_chart(data, theme, legend):
    deployment_id = data["id"]
    new_figure = html.Div()
    device_type = data["role"]
    if device_type in get_supported_chart_types().keys():
        fn = get_supported_chart_types(legend)[device_type]
        new_figure = fn(deployment_id, theme)

    return new_figure
