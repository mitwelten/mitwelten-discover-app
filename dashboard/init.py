import json
from functools import reduce

from dashboard.config.map import DEFAULT_MARKER_COLORS
from dashboard.api.api_client import get_environment_data, get_environment_legend, get_deployments
from dashboard.model.deployment import Deployment


URL_DEPLOYMENTS = "https://data.mitwelten.org/api/v3/deployments"


def init_deployment_data():
    all_deployments_json = [d for d in get_deployments()]

    all_deployments = [Deployment(d) for d in all_deployments_json]

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
