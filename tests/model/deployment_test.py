import unittest

from src.model.deployment import Deployment

json_deployment = {
    "deployment_id": 1,
    "node_id": 76,
    "location": {
        "lat": 47.53514,
        "lon": 7.61467
    },
    "description": "on a sidewall of a storage building in the Merian Gardens",
    "period": {
        "start": "2021-03-15T23:00:00+00:00",
        "end": "2021-04-20T22:00:00+00:00"
    },
    "tags": [
        {
            "tag_id": 135,
            "name": "FS1"
        }
    ],
    "node": {
        "node_id": 76,
        "node_label": "7758-4041",
        "type": "Audio Logger",
        "serial_number": "24E144085F256998",
        "description": "renamed from AM1",
        "platform": "AudioMoth",
        "connectivity": "null",
        "power": "null",
        "hardware_version": "null",
        "software_version": "null",
        "firmware_version": "null"
    }
}


class MyTestCase(unittest.TestCase):
    def test_something(self):

        depl = Deployment(json_deployment)
        depl_dict = depl.to_dict()
        depl = Deployment(depl_dict)

        self.assertEqual(depl.id, depl_dict["id"])
        self.assertEqual(depl.description, depl_dict["description"])
        self.assertEqual(depl.lat, depl_dict["location"]["lat"])
        self.assertEqual(depl.lon, depl_dict["location"]["lon"])
        self.assertEqual(depl.period_end, depl_dict["period"]["end"])
        self.assertEqual(depl.period_start, depl_dict["period"]["start"])
        self.assertEqual(depl.node_type, depl_dict["node"]["type"])
        self.assertEqual(depl.node_label, depl_dict["node"]["node_label"])
        for idx, tag in enumerate(depl.tags):
            self.assertEqual(tag, depl_dict["tags"][idx]["name"])


if __name__ == '__main__':
    unittest.main()
