
from src.model.file import File

empty_note = dict(
    note_id="",
    node_label="",
    title="",
    description="",
    location=dict(
        lat=0,
        lon=0
    ),
    date="",
    author="",
    public=False,
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
        self.date = json_note.get("date")
        p = json_note.get("public", False)
        if isinstance(p, bool):
            self.public = p
        else:
            self.public = True if "true" in str(p).lower() else False,
        self.author= json_note.get("author")

    def __eq__(self, other):
        return (self.id == other.id and
                self.title == other.title and
                self.description == other.description and
                self.author== other.author and
                self.date == other.date and
                self.author == other.author and
                self.public == other.public and
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
            date=self.date,
            author=self.author,
            public=self.public,
            files=[f.to_dict() for f in self.files] if self.files is not None else []
        )
