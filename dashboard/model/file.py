class File:
    def __init__(self, json_file):
        self.id = json_file.get("id")
        self.name = json_file.get("name")
        self.type = json_file.get("type")
        self.last_modified = json_file.get("last_modified")

    def __eq__(self, other):
        return (
            self.id == other.id and
            self.name == other.name and
            self.type == other.type and
            self.last_modified == other.last_modified
        )

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            type=self.type,
            last_modified=self.last_modified
        )
