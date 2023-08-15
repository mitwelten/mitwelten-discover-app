import json
from datetime import datetime
from functools import reduce

from dashboard.config.map import DEFAULT_MARKER_COLORS
from dashboard.api.api_client import get_environment_data, get_environment_legend, get_deployments
from dashboard.model.deployment import Deployment

def get_tag(start, end):
    result = []
    start_y = datetime.fromisoformat(start).year
    start_m = datetime.fromisoformat(start).month

    if start_y == 2022 and start_m < 11:
        result.append(2)
    if start_y == 2021 and start_m < 11:
        result.append(1)
    if end is None:
        result.append(3)
    else:
        end_y = datetime.fromisoformat(end).year
        end_m = datetime.fromisoformat(end).month
        if end_y == 2022 and end_m > 11:
            result.remove(3)
        if end_y == 2021 and end_m > 11:
            result.remove(2)
        if end_y == 2023:
            result.append(3)

    return sorted(result)



def init_deployment_data():
    all_deployments_json = [d for d in get_deployments()]

    all_deployments = [Deployment(d) for d in all_deployments_json]
    tag_less = filter(lambda d: "FS1" not in d.tags and "FS2" not in d.tags and "FS3" not in d.tags, all_deployments)
    for d in tag_less:
        print(f"[] "
              f"id: {d.deployment_id} - "
              f"node_label: {d.node_label} - "
              f"start: {datetime.fromisoformat(d.period_start).date()} - "
              f"end: {datetime.fromisoformat(d.period_end).date() if d.period_end is not None else ''} - "
              f"tag: {get_tag(d.period_start, d.period_end)}")

    all_types = set(map(lambda d: d.node_type, all_deployments))

    all_tags = map(lambda d: d.tags, all_deployments)
    all_tags = sorted(set(reduce(list.__add__, all_tags)))
    tags = json.dumps(all_tags)

    # {type: color}
    deployment_markers = {}
    idx_list = enumerate(sorted(all_types))
    for (idx, node_type) in idx_list:
        deployment_markers[node_type] = dict(
            color=DEFAULT_MARKER_COLORS[idx],
            svgPath=f"assets/markers/location-{idx}.svg"
        )

    # {type: deployment}
    deployment_dict = {}
    for node_type in all_types:
        deployment_dict[node_type] = [
            d for d in all_deployments_json
            if node_type.lower().strip() in d["node"]["type"].lower()
        ]

    return deployment_dict, deployment_markers, tags


def init_environment_data():
    all_environments_json = get_environment_data()
    environment_legend = get_environment_legend()

    return all_environments_json, environment_legend
