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

    
    if args.get("zoom") is None:
        args["zoom"] = 12

    if args.get("lat") is None or args.get("lon") is None:
        args["lat"] = 47.5339807306196
        args["lon"] = 7.6169566067567

    if args.get("tags") is None:
        args["tags"] = []

    if args.get("fs") is None:
        args["fs"] = "ANY"

    return args
