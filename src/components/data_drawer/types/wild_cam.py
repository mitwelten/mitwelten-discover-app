
from datetime import datetime, timedelta

from dash import html, Output, Input, State, ctx, ALL, ClientsideFunction, no_update
from src.main import app
import plotly.graph_objects as go
from dash import dcc
import dash_mantine_components as dmc
from src.model.deployment import Deployment

from src.api.api_deployment import get_audio_timeseries
from src.components.data_drawer.header import bottom_drawer_content
from src.components.data_drawer.charts import create_themed_figure


def create_wild_cam_view(deployment_data, theme):
    d = Deployment(deployment_data)
    print(deployment_data)


    view = dmc.Image(id="id-wild-cam-image")

    return [
        dcc.Store("id-wild-cam-image-store", data=deployment_data["id"]),
        bottom_drawer_content("Wild Cam", "tbd", d.tags, "camera1.svg", theme, True), 
        dmc.Paper(
            children=view,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        ),
    ]

app.clientside_callback(
    ClientsideFunction(
       namespace="attachment", function_name="singleImage"
    ),
    Output("id-wild-cam-image", "src"),
    Input("id-wild-cam-image-store", "data"),
)
