class Note:
    def __init__(self, json_note):
        self.note_id = json_note.get("note_id")
        self.title = json_note.get("title")
        self.description = json_note.get("description")
        self.node_label = json_note.get("node_label")
        location = json_note.get("location")
        self.lat = location.get("lat")
        self.lon = location.get("lon")
        self.tags = (
            [t.get("name") for t in json_note.get("tags")]
            if json_note.get("tags") is not None
            else []
        )
        self.created_at = json_note.get("created_at")
        self.updated_at = json_note.get("updated_at")
        self.file_ids = json_note.get("file_ids")