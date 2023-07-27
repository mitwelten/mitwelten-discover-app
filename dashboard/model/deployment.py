import json


class Deployment:

    def __init__(self, deployment_response: dict):
        self.deployment_id = deployment_response.get("deployment_id")
        description = deployment_response.get("description")
        self.description = description if description else "-"
        self.node_label = deployment_response.get("node").get("node_label")
        self.node_type = deployment_response.get("node").get("type")
        period = deployment_response.get("period")
        self.period_start = period.get("start")
        self.period_end = period.get("end")
        self.tags = (
            [t.get("name") for t in deployment_response.get("tags")]
            if deployment_response.get("tags") is not None
            else []
        )
        location = deployment_response.get("location")
        self.lat = location.get("lat")
        self.lon = location.get("lon")

    def __str__(self):
        return f"id: {self.deployment_id}\n" \
               f"node_label: {self.node_label}\n" \
               f"node_type: {self.node_type}\n" \
               f"lat: {self.lat}\t" \
               f"lon: {self.lon}\n" \
               f"from: {self.period_start} to {self.period_end}\n"

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
