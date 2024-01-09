class Tag:
    def __init__(self, json_tag):
        self.name = json_tag.get("name")

    def to_dict(self):
        return dict(name=self.name)


