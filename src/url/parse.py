from src.model.environment import Environment
from src.model.note import Note
from src.model.url_parameter import UrlParameter
from src.model.deployment import Deployment
from src.util.helper_functions import was_deployed
from src.config.app_config import QUERY_PARAMS

# deployments = {"type": [deployments]}
def get_device_from_deployments(params: UrlParameter, deployments):
    all_deployments = []

    for key in deployments.keys():
        all_deployments += deployments[key]

    canditates: list[Deployment] = []
    for depl in all_deployments:
        d = Deployment(depl)
        if d.node_label == params.node_label:
            canditates.append(d)

    canditates = list(filter(lambda x: was_deployed(x, params.start, params.end), canditates))
    canditates = sorted(canditates, key=lambda x: x.period_start)
    if len(canditates) > 0:
        return canditates[-1]
    return None


def get_device_from_notes(params: UrlParameter, notes):
    for note in notes:
        if params.note_id == str(note["id"]):
            return Note(note)


def get_device_from_env(params: UrlParameter, envs):
    for env in envs:
        if params.env_id == str(env["id"]):
            return Environment(env)


def get_device_from_params(params: UrlParameter, deployments, notes, env):
    if params.node_label is not None:
        return get_device_from_deployments(params, deployments)
    elif params.note_id is not None:
        return get_device_from_notes(params, notes)
    elif params.env_id is not None:
        return get_device_from_env(params, env)
    else:
        return None
    

def _get_value_or_none(param, data):
    if data.get(param) is not None and data[param]:
        if isinstance(data[param], list):
            return f"{param}={','.join(data[param])}"
        else:
            return f"{param}={data[param]}"
    return None


def query_data_to_string(data):
    # special case: if timerange is set, remove start and end (happens on startup)
    if data.get("timerange") is not None:
        if data.get("start") is not None:
            del data["start"]
        if data.get("end") is not None:
            del data["end"]

    params : list[str] = []

    # TODO: replace keys with class attributes
    for key in QUERY_PARAMS.keys():
        param = _get_value_or_none(key, data)
        if param is not None and param != "":
            params.append(param)

    return "?" + "&".join(params)


def update_query_data(data, params: dict):
    # update data dict with params
    for param in params.keys():
        if params.get(param) is not None:
            data[param] = params[param]
        else:
            if data.get(param) is not None:
                del data[param]

    return dict(sorted(data.items()))

