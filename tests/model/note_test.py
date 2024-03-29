import unittest
from datetime import datetime

from src.model.file import File
from src.model.note import Note, empty_note

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
    "public": "true",
    "tags": [
        {
            "name": "FS1"
        },
        {
            "name": "Am Wasser"
        }
    ],
    "files": [
        {
            "type": "image/png",
            "name": "test_img.png",
            "object_name": "test_img.png"
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
        self.assertEqual(note.public, note_dict["public"])
        for idx, tag in enumerate(note.tags):
            self.assertEqual(tag, note_dict["tags"][idx]["name"])


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
        note1.author = "tester"
        note2.author = "tester"
        note1.title = "test case"
        note2.title = "test case"
        note1.description = "this is a test case"
        note2.description = "this is a test case"
        note1.date = test_date
        note2.date = test_date
        note1.public = True
        note2.public = True
        note1.files = [test_file, test_file]
        note2.files = [test_file, test_file]
        self.assertTrue(note1 == note2)


if __name__ == '__main__':
    unittest.main()
