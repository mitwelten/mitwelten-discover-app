class Tag:
    def __init__(self, json_tag):
        self.id = json_tag.get("note_id", json_tag.get("id"))
        self.name = json_tag.get("name")

    def to_dict(self):
        return dict(
            id=self.id,
            title=self.name)



