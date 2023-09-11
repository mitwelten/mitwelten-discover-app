import unittest

from dashboard.model.note import Note

json_note = {
    "note_id": 0,
    "node_label": "1000-0001",
    "title": "This is the Title of the Note",
    "description": "Awesome description of the note Awesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the note",
    "location": {
        "lat": 47.53514,
        "lon": 7.61467
    },
    "created_at": "2021-03-15T23:00:00+00:00",
    "updated_at": "2021-04-20T22:00:00+00:00",
    "creator": "Andri Wild",
    "tags": [{
        "tag_id": 135,
        "name": "FS1"
        },
        {
            "tag_id": 7,
            "name": "Am Wasser"
        }
    ],
    "files": [
        {
            "id": 20,
            "name": "The Book",
            "type": "pdf",
            "last_modified": "2021-03-15T23:00:00+00:00"
        },
        {
            "id": 23,
            "name": "Mitwelten Logo",
            "type": "png",
            "last_modified": "2021-03-12T23:00:00+00:00"
        }
    ]
}


class TestNote(unittest.TestCase):

    def test_to_dict(self):
        note = Note(json_note)
        note_dict = note.to_dict()
        note = Note(note_dict)

        self.assertEqual(note.id, note_dict["id"])
        self.assertEqual(note.title, note_dict["title"])
        self.assertEqual(note.description, note_dict["description"])
        self.assertEqual(note.lat, note_dict["location"]["lat"])
        self.assertEqual(note.lon, note_dict["location"]["lon"])
        self.assertEqual(note.creator, note_dict["creator"])
        self.assertEqual(note.created_at, note_dict["created_at"])
        self.assertEqual(note.updated_at, note_dict["updated_at"])
        for idx, tag in enumerate(note.tags):
            self.assertEqual(tag, note_dict["tags"][idx]["name"])

        for idx, file in enumerate(note.files):
            self.assertEqual(file.id, note_dict["files"][idx]["id"])


if __name__ == '__main__':
    unittest.main()
