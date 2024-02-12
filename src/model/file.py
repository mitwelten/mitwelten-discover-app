class File:
    def __init__(self, json_file):
        self.id= json_file.get("id")
        self.name = json_file.get("name")
        self.type = json_file.get("type")
        self.object_name = json_file.get("object_name")

    def __eq__(self, other):
        return (
                self.id == other.id and
                self.name == other.name and
                self.type == other.type and
                self.object_name == other.object_name
        )

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            type=self.type,
            object_name=self.object_name
        )
