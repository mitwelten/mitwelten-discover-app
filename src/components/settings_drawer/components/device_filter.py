from src.model.deployment import Deployment
from src.config.id_config import *
from src.main import app
from dash import Output, Input, State, ALL, ctx, no_update
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from src.model.base import BaseDeployment
from pprint import pprint

def device_filter(active_device: BaseDeployment):

    return dmc.Select(
            id="id-device-select",
            withScrollArea=True,
            searchable=True,
            clearable=True,
            nothing_found="No ID found",
            placeholder="Select an ID"
            )


@app.callback(
        Output("id-device-select", "data"),
        Output("id-device-select", "value"),
        Output(ID_DEVICE_FILTER_STORE, "data"),
        Input(ID_VISIBLE_DEPLOYMENT_STORE, "data"),
        Input(ID_VISIBLE_NOTE_STORE, "data"),
        Input(ID_VISIBLE_ENV_STORE, "data"),
        State(ID_DEVICE_FILTER_STORE, "data"),
        prevent_initial_call=True,
        )
def update_select_data(depls, notes, envs, init):
    data = [
            {
                "group" : "Deployments",             
                "items": list(sorted(set(depls.get("deployments"))))
            },
            {
                "group" : "Experiment and Findings", 
                "items": list(map(lambda x: {"value": f"note-{x}", "label": str(x)}, sorted(notes.get("notes"))))
            },
            {
                "group" : "Habitat Types",           
                "items": list(map(lambda x: {"value": f"env-{x}", "label": str(x)}, sorted(envs.get("envs"))))
            }
        ]
    if init.get("id") is not None:
        return data, init.get("id"), dict(id=None) 
    return data, no_update, no_update

