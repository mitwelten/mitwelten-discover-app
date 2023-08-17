import json
from datetime import datetime
from functools import reduce

from dashboard.config.map import DEFAULT_MARKER_COLORS
from dashboard.api.api_client import get_environment_data, get_environment_legend, get_deployments, get_all_fake_notes
from dashboard.model.deployment import Deployment


def init_deployment_data():
    all_deployments_json = [d for d in get_deployments()]
    all_deployments = [Deployment(d) for d in all_deployments_json]

    all_types = set(map(lambda d: d.node_type, all_deployments))

    all_tags = map(lambda d: d.tags, all_deployments)
    all_tags = sorted(set(reduce(list.__add__, all_tags)))
    tags = json.dumps(all_tags)

    # {type: color}
    data_sources = {}
    all_types = sorted(all_types)

    # {type: deployment}
    deployment_dict = {}
    for node_type in all_types:
        deployment_dict[node_type] = [
            d for d in all_deployments_json
            if node_type.lower().strip() in d["node"]["type"].lower()
        ]

    idx_list = enumerate(all_types)
    for (idx, node_type) in idx_list:
        data_sources[node_type] = dict(
            color=DEFAULT_MARKER_COLORS[idx],
            svgPath=f"assets/markers/location-{idx}.svg"
        )

    data_sources["Notes"] = dict(color="#ffd800", svgPath="assets/markers/note.svg")
    data_sources["Environment Data Points"] = dict(color="#946000", svgPath="assets/markers/environment.svg")

    return deployment_dict, data_sources, tags


def init_environment_data():
    all_environments_json = get_environment_data()
    environment_legend = get_environment_legend()

    return all_environments_json, environment_legend


def init_notes():
    all_notes = get_all_fake_notes()
    return all_notes
