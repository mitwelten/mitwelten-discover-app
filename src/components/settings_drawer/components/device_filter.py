from src.config.id_config import *
import dash_mantine_components as dmc
from src.model.base import BaseDeployment
from pprint import pprint

def device_filter(active_device: BaseDeployment, deployments):
    active_id = active_device.id if active_device else None
    all_labels = []
    value = None

    for key in deployments.keys():
        for depl in deployments[key]:
            label = depl.get("node",{}).get("node_label")
            all_labels.append(label)
            if depl.get("id") == active_id:
                value = label

    all_labels = list(sorted(set(all_labels)))

    print("active_device")
    print(active_device.id if active_device else None)

    return dmc.Select(
            id=ID_DEVICE_SELECT,
            value=value,
            data=all_labels,
            withScrollArea=True,
            searchable=True,
            clearable=True,
            nothingFoundMessage="No label found",
            placeholder="Node Label"
            )

