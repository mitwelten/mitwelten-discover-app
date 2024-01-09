class Environment:

    def __init__(self, environment_json: dict):
        self.id = environment_json.get("environment_id", environment_json.get("id"))
        location = environment_json.get("location")
        self.lat = location.get("lat")
        self.lon = location.get("lon")
        self.created_at = environment_json.get("created_at")
        self.updated_at = environment_json.get("updated_at")
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
        return f"id: {self.id}\n" \
               f"lat: {self.lat}\t" \
               f"lon: {self.lon}\n" \


    def to_dict(self):
        return dict(
            id=self.id,
            location=dict(lat=self.lat, lon=self.lon),
            created_at=self.created_at,
            updated_at=self.updated_at,
            attribute_01=self.attribute_01,
            attribute_02=self.attribute_02,
            attribute_03=self.attribute_03,
            attribute_04=self.attribute_04,
            attribute_05=self.attribute_05,
            attribute_06=self.attribute_06,
            attribute_07=self.attribute_07,
            attribute_08=self.attribute_08,
            attribute_09=self.attribute_09,
            attribute_10=self.attribute_10
        )

