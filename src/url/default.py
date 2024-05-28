from src.config.app_config import QUERY_PARAMS
from src.config.settings_config import FIRST_DEPLOYMENT_WEEKS_AGO
from datetime import datetime, timedelta

def set_default_args(args):
    timerange = args.get("timerange")
    if  timerange is None:
        if args.get("start") is None or args.get("end") is None:
            args["start"] = (datetime.now() - timedelta(weeks=FIRST_DEPLOYMENT_WEEKS_AGO)).isoformat(timespec="seconds")
            args["end"]   = datetime.now().isoformat(timespec="seconds")
    else:
       args["start"] = (datetime.now() - timedelta(weeks=int(timerange))).isoformat(timespec="seconds")
       args["end"]   = datetime.now().isoformat(timespec="seconds")

    if args.get("devices") is not None:
        args["devices"] = args["devices"].replace(" ", "+")

    if args.get("tags") is not None:
        args["tags"] = args["tags"].replace(" ", "+")

    tmp = QUERY_PARAMS.copy()
    tmp.update(args)
    return tmp 
