from dash_iconify import DashIconify
import dash_mantine_components as dmc
from src.config.app_config import *

def deployment_icon(file_name):
    return dmc.Image(
            src=f"assets/markers/{file_name}.svg",
            alt=f"{file_name} icon", 
            style={"minWidth": "25px", "width": "50px"}
            )


deployment_info = dmc.List(
    size="sm",
    spacing="lg",
    children=[
        dmc.ListItem(PAX_DESCRIPTION, icon=deployment_icon("paxCounter")),
        dmc.ListItem(AUDIO_DESCRIPTION, icon=deployment_icon("audioLogger")),
        dmc.ListItem(POLLINATOR_DESCRIPTION, icon=deployment_icon("polliCam")),
        dmc.ListItem(ENVIRONMENT_SENSOR_DESCRIPTION, icon=deployment_icon("environSensor")),
        dmc.ListItem(HABITAT_DESCRIPTION, icon=deployment_icon("habitat")),
        dmc.ListItem(EXPERIMENT_AND_FINDING_DESCRIPTION, icon=deployment_icon("docu")),
        dmc.ListItem(WILD_CAM_DESCRIPTION, icon=deployment_icon("wildCam")),
    ],
)
