from src.model.base import BaseDeployment


class Deployment(BaseDeployment):

    def __init__(self, json_deployment: dict):
        id = json_deployment.get("deployment_id", json_deployment.get("id"))

        location = json_deployment.get("location", {})
        lat = location.get("lat")
        lon = location.get("lon")

        node_type = json_deployment.get("node", {}).get("type").replace(".","")  # replace the dot (.) in Env. Sensor, based on callback issues

        super().__init__(id, lat, lon, node_type)

        self.id = id
        description = json_deployment.get("description")
        self.description = description if description else ""
        self.node_label = json_deployment.get("node", {}).get("node_label")
        self.node_type = node_type
        period = json_deployment.get("period", {})
        self.period_start = period.get("start")
        self.period_end = period.get("end")
        self.tags = (
            [t.get("name") for t in json_deployment.get("tags", {})]
            if json_deployment.get("tags") is not None
            else []
        )
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f"id: {self.id}\n" \
               f"node_label: {self.node_label}\n" \
               f"node_type: {self.node_type}\n" \
               f"lat: {self.lat}\t" \
               f"lon: {self.lon}\n" \
               f"from: {self.period_start} to {self.period_end}\n"

    def to_dict(self):
        return dict(
            id=self.id,
            description=self.description,
            node=dict(node_label=self.node_label, type=self.node_type),
            location=dict(lat=self.lat, lon=self.lon),
            tags=[{"name": t} for t in self.tags] if self.tags is not None else [],
            period=dict(start=self.period_start, end=self.period_end),
        )
