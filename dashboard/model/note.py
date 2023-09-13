
from dashboard.model.file import File

empty_note = dict(
    note_id="",
    node_label="",
    title="",
    description="",
    location=dict(
        lat=0,
        lon=0
    ),
    created_at="",
    updated_at="",
    creator="",
    tags=[],
    files=[]
    )


class Note:
    def __init__(self, json_note):
        self.id = json_note.get("note_id", json_note.get("id"))
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
        self.files = (
            [File(t) for t in json_note.get("files")]
            if json_note.get("files") is not None
            else []
        )
        self.created_at = json_note.get("created_at")
        self.updated_at = json_note.get("updated_at")
        self.creator = json_note.get("creator")

    def __eq__(self, other):
        return (self.id == other.id and
                self.title == other.title and
                self.description == other.description and
                self.creator == other.creator and
                self.created_at == other.created_at and
                self.updated_at == other.updated_at and
                self.lat == other.lat and
                self.lon == other.lon and
                self.node_label == other.node_label and
                self.files == other.files and
                self.tags == other.tags
                )


    def to_dict(self):
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            note_label=self.node_label,
            location=dict(lat=self.lat, lon=self.lon),
            tags=[{"name": t} for t in self.tags] if self.tags is not None else [],
            created_at=self.created_at,
            updated_at=self.updated_at,
            creator=self.creator,
            files=[f.to_dict() for f in self.files] if self.files is not None else []
        )
