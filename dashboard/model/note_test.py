import unittest
from datetime import datetime

from dashboard.model.file import File
from dashboard.model.note import Note, empty_note

json_note = {
    "note_id": 0,
    "node_label": "1000-0001",
    "title": "This is the Title of the Note",
    "description": "Awesome description of the note Awesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the note",
    "location": {
        "lat": 47.53514,
        "lon": 7.61467
    },
    "date": "2021-03-15T23:00:00+00:00",
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
        self.assertEqual(note.author, note_dict["author"])
        self.assertEqual(note.date, note_dict["date"])
        for idx, tag in enumerate(note.tags):
            self.assertEqual(tag, note_dict["tags"][idx]["name"])

        for idx, file in enumerate(note.files):
            self.assertEqual(file.id, note_dict["files"][idx]["id"])

    def test_eq_with_emtpy_notes(self):
        note1 = Note(empty_note)
        note2 = Note(empty_note)
        self.assertTrue(note1 == note2)

    def test_eq_should_fail(self):
        note1 = Note(empty_note)
        note1.id = 123
        note2 = Note(empty_note)
        self.assertTrue(note1 != note2)

    def test_eq_with_filled_properties(self):
        note1 = Note(empty_note)
        note2 = Note(empty_note)
        test_file = File(dict(id="1", name="testfile", last_modified=datetime.now().isoformat(), type="pdf"))
        test_date = datetime.now().isoformat()
        note1.tags = [dict(name="test"), dict(name="test2")]
        note2.tags = [dict(name="test"), dict(name="test2")]
        note1.node_label = "test case"
        note2.node_label = "test case"
        note1.creator = "tester"
        note2.creator = "tester"
        note1.title = "test case"
        note2.title = "test case"
        note1.description = "this is a test case"
        note2.description = "this is a test case"
        note1.date = test_date
        note1.files = [test_file, test_file]
        note2.files = [test_file, test_file]
        self.assertTrue(note1 == note2)


if __name__ == '__main__':
    unittest.main()
