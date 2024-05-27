from src.model.deployment import Deployment
from urllib import parse 
from src.util.helper_functions import was_deployed

def get_device_from_args(args, deployments, notes, env_data):
    types = {
            "node_label": deployments, 
            "note_id": notes, 
            "env_id": env_data
            }

    names      = list(types.keys())
    active_idx = 0
    active_id  = args.get(names[active_idx])

    i = 1
    while i < len(names) and active_id == None:
        current_id = args.get(names[i])
        if current_id is not None:
            active_id = current_id
            active_idx = i
        i += 1

    if active_id == None:
        return None

    active_name = names[active_idx]


    is_deployment = active_name == "node_label"
    elems = []

    if is_deployment:
        for key in deployments.keys():
            elems += deployments[key]
    else:
        elems = types[active_name]

    current_id = None
    index      = 0
    found      = False
    while not found and index < len(elems):
        if is_deployment:
            current_id = elems[index]["node"][active_name]
        else:
            current_id = elems[index]["id"]

        if str(current_id) == str(active_id):
            if is_deployment:
                d = Deployment(elems[index])
                found = was_deployed(d, args["start"], args["end"])
            else:
                found = True

        index += 1

    return elems[index - 1] if index < len(elems) else None


def get_value_or_none(param, data):

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

    # TODO: move to config
    query_params = [
            "start", 
            "end", 
            "timerange", 
            "fs", 
            "lat", 
            "lon", 
            "zoom", 
            "tags", 
            "devices", 
            "node_label", 
            "note_id", 
            "env_id"
            ]

    params : list[str] = []

    for key in query_params:
        param = get_value_or_none(key, data)
        if param is not None and param != "":
            params.append(param)

    return "?" + "&".join(params)


def query_string_to_dict(query:str):
    if len(query) > 0 and query[0] == "?":
        query = query[1:] # remove the question mark
    params = parse.parse_qs(query)
    return {k: v[0] for k,v in params.items()}


def update_query_data(data, params: dict):
    # update data dict with params
    for param in params.keys():
        if params[param] is not None:
            data[param] = params[param]
        else:
            if data.get(param) is not None:
                del data[param]

    return dict(sorted(data.items()))
