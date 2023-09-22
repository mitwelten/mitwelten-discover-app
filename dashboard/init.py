from dashboard.api.api_deployment import get_deployments, get_tags
from dashboard.api.api_environment import get_environment_data, get_environment_legend
from dashboard.api.api_note import get_all_notes
from dashboard.model.deployment import Deployment
from dashboard.model.environment import Environment
from dashboard.model.note import Note
from dashboard.model.tag import Tag


def init_deployment_data():
    all_deployments_json = [d for d in get_deployments()]
    all_deployments = [Deployment(d) for d in all_deployments_json]

    all_types = set(map(lambda d: d.node_type, all_deployments))

    # {type: color}
    all_types = sorted(all_types)

    # {type: deployment}
    deployment_dict = {}
    for node_type in all_types:
        deployment_dict[node_type] = [
            d.to_dict() for d in all_deployments
            if node_type.lower().strip() in d.node_type.lower()
        ]

    return deployment_dict


def init_environment_data():
    all_environments_json = get_environment_data()
    # standardize dictionary properties
    all_environments = [Environment(env).to_dict() for env in all_environments_json]
    environment_legend = get_environment_legend()
    return all_environments, environment_legend


def init_notes(auth_cookie=None):
    all_notes = get_all_notes(auth_cookie)
    # standardize dictionary properties
    all_notes = [Note(n).to_dict() for n in all_notes]
    return all_notes


def init_tags():
    all_tags = get_tags()
    # standardize dictionary properties
    all_tags = [Tag(t).to_dict() for t in all_tags]
    return all_tags
