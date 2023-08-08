import json


class Environment:

    def __init__(self, environment_response: dict):
        self.environment_id = environment_response.get("environment_id")
        location = environment_response.get("location")
        self.lat = location.get("lat")
        self.lon = location.get("lon")
        self.created_at = environment_response.get("created_at")
        self.updated_at = environment_response.get("updated_at")
        self.attribute_01 = location.get("attribute_01")
        self.attribute_02 = location.get("attribute_02")
        self.attribute_03 = location.get("attribute_03")
        self.attribute_04 = location.get("attribute_04")
        self.attribute_05 = location.get("attribute_05")
        self.attribute_06 = location.get("attribute_06")
        self.attribute_07 = location.get("attribute_07")
        self.attribute_08 = location.get("attribute_08")
        self.attribute_09 = location.get("attribute_09")
        self.attribute_10 = location.get("attribute_10")

    def __str__(self):
        return f"id: {self.environment_id}\n" \
               f"lat: {self.lat}\t" \
               f"lon: {self.lon}\n" \


    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
