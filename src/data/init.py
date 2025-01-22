from src.config.app_config import EXCLUDED_DEPLOYMENTS
from src.api.api_deployment import get_deployments, get_tags
from src.api.api_environment import get_environment_data, get_environment_legend
from src.api.api_note import get_all_notes
from src.model.deployment import Deployment
from src.model.environment import Environment
from src.model.note import Note
from src.model.tag import Tag


def init_deployment_data():
    all_deployments_json = get_deployments()

    all_deployments = [Deployment(d) for d in all_deployments_json or []]

    # filter out deployments with "Bats" in the tags
    all_deployments = [d for d in all_deployments
                       if not (d.node_type == "Audio Logger" and "Bats" in d.tags)
                       and not "Critical Media Lab" in d.tags
                       ]

    # change type Phaeno Cam to Wild Cam
    for d in all_deployments:
        if d.node_type == "Phaeno Cam":
            d.node_type = "Wild Cam"

    all_types = sorted(set(map(lambda d: d.node_type, all_deployments)))
    excluded  = [excl.lower().strip() for excl in EXCLUDED_DEPLOYMENTS]

    all_types_filtered = []
    for depl_type in all_types.copy():
        if depl_type.lower().strip() not in excluded:
            all_types_filtered.append(depl_type)


    # {type: deployments}
    deployment_dict = {}
    for source_type in all_types_filtered:
        deployment_dict[source_type] = [
            d.to_dict() for d in all_deployments
            if source_type.lower().strip() in d.node_type.lower()
        ]

    return deployment_dict


env_legend_en = {
        "Gewässer" : "Aquatic environment",
        "Blühangebot" : "Availability of flowers",
        "Substratvorkommen" : "Availability of substrate",
        "Nistmöglichkeit" : "Nesting opportunity",
        "Fragmentierung" : "Fragmentation",
        "Habitatvielfalt" : "Habitat diversity",
        "Pflanzenvielfalt" : "Plant diversity",
        "Siedlungsfaktor" : "Settlement factor",
        "Bodenversiegelung" : "Soil sealing",
        "Sonneneinstrahlung" : "Solar radiation",
        }

def translate_lables(legend):
    for key in legend.keys():
        legend[key]["label"] = env_legend_en[legend[key]["label"]]
    return legend


def init_environment_data():
    all_environments_json = get_environment_data()
    if all_environments_json is None:
        return [], []
    # standardize dictionary properties
    all_environments = [Environment(env).to_dict() for env in all_environments_json]
    environment_legend = get_environment_legend()
    environment_legend = translate_lables(environment_legend)
    return all_environments, environment_legend



def init_notes(auth_cookie=None) -> list[dict]:
    all_notes = get_all_notes(auth_cookie)
    # standardize dictionary properties
    all_notes = [Note(n).to_dict() for n in all_notes]
    return all_notes


def init_tags():
    all_tags = get_tags()
    if all_tags is None:
        return []
    # standardize dictionary properties
    all_tags = [Tag(t).to_dict() for t in all_tags]
    return all_tags

