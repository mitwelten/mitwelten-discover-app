import json
from functools import reduce

import requests

from dashboard.config import api_config, map_config
from dashboard.model.deployment import Deployment


def init_app_data():
    all_deployments_json = [d for d in requests.get(api_config.URL_DEPLOYMENTS).json()]
    all_deployments = [Deployment(d) for d in all_deployments_json]

    all_types = set(map(lambda d: d.node_type, all_deployments))

    all_tags = map(lambda d: d.tags, all_deployments)
    all_tags = sorted(set(reduce(list.__add__, all_tags)))
    tags = json.dumps(all_tags)

    # {type: color}
    deployment_colors = {}
    idx_list = enumerate(sorted(all_types))
    for (idx, node_type) in idx_list:
        deployment_colors[node_type] = map_config.DEFAULT_MARKER_COLORS[idx]

    # {type: deployment}
    deployment_dict = {}
    for node_type in all_types:
        deployment_dict[node_type] = [
            d for d in all_deployments_json
            if node_type.lower().strip() in d["node"]["type"].lower()
        ]

    return deployment_dict, deployment_colors, tags
