from dataclasses import dataclass
from src.config.map_config import DEFAULT_LAT, DEFAULT_LON
from src.config.settings_config import FIRST_DEPLOYMENT_WEEKS_AGO
from datetime import datetime, timedelta

default_start = (datetime.now() - timedelta(weeks=FIRST_DEPLOYMENT_WEEKS_AGO)).isoformat(timespec="seconds")
default_end = datetime.now().isoformat(timespec="seconds")

@dataclass
class UrlParameter():

    def __init__(self, json):
        self.timerange = json.get("timerange", "1") or "1"
        
        if self.timerange != "custom":
            self.start = (datetime.now() - timedelta(weeks=int(self.timerange))).isoformat(timespec="seconds")
            self.end   = datetime.now().isoformat(timespec="seconds")
        else:
            self.start = json.get("start", default_start)
            self.end = json.get("end", default_end)

        self.lat = json.get("lat", DEFAULT_LAT)
        self.lon = json.get("lon", DEFAULT_LON)
        self.zoom = int(float(json.get("zoom", 12)))
        self.devices = self.parse_param_list(json, "devices")
        self.tags = self.parse_param_list(json, "tags")
        self.node_label = json.get("node_label")
        self.note_id = json.get("note_id")
        self.env_id = json.get("env_id")
        self.map = json.get("map", 0)
        self.overlay = json.get("overlay", 0)


    def parse_param_list(self, args: dict, key: str) -> list[str] | None:
        devices_string = args.get(key)

        if devices_string is not None:
            devices = devices_string.split(" ")
            return list(map(lambda d: d.replace("_", " "), devices))
        return None


    def to_dict(self):
        if self.devices is not None:
            devices = "+".join(self.devices)
            devices = devices.replace(" ", "_")
        else:
            devices = None

        if self.tags is not None:
            tags = "+".join(self.tags)
            tags = tags.replace(" ", "_")
        else:
            tags = None

        return dict(
            start=self.start,
            end=self.end,
            timerange=self.timerange,
            lat=self.lat,
            lon=self.lon,
            zoom=self.zoom,
            tags=tags,
            devices=devices,
            node_label=self.node_label,
            note_id=self.note_id,
            env_id=self.env_id,
            map=self.map,
            overlay=self.overlay
        )

