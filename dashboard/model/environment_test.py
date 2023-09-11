import unittest

from dashboard.model.environment import Environment

json_env = {
    "environment_id": 0,
    "location": {
        "lat": 47.53484943172696,
        "lon": 7.612519197679952
    },
    "timestamp": "2023-09-11T10:45:42.938Z",
    "attribute_01": 0,
    "attribute_02": 0,
    "attribute_03": 0,
    "attribute_04": 0,
    "attribute_05": 0,
    "attribute_06": 0,
    "attribute_07": 0,
    "attribute_08": 0,
    "attribute_09": 0,
    "attribute_10": 0,
    "created_at": "2023-09-11T10:45:42.939Z",
    "updated_at": "2023-09-11T10:45:42.939Z",
    "distance": 0
}


class MyTestCase(unittest.TestCase):
    def test_to_dict(self):
        env = Environment(json_env)
        env_dict = env.to_dict()
        self.assertEqual(env.id, env_dict["id"])
        self.assertEqual(env.lat, env_dict["location"]["lat"])
        self.assertEqual(env.lon, env_dict["location"]["lon"])
        self.assertEqual(env.created_at, env_dict["created_at"])
        self.assertEqual(env.updated_at, env_dict["updated_at"])
        self.assertEqual(env.attribute_01, env_dict["attribute_01"])
        self.assertEqual(env.attribute_02, env_dict["attribute_02"])
        self.assertEqual(env.attribute_03, env_dict["attribute_03"])
        self.assertEqual(env.attribute_04, env_dict["attribute_04"])
        self.assertEqual(env.attribute_05, env_dict["attribute_05"])
        self.assertEqual(env.attribute_06, env_dict["attribute_06"])
        self.assertEqual(env.attribute_07, env_dict["attribute_07"])
        self.assertEqual(env.attribute_08, env_dict["attribute_08"])
        self.assertEqual(env.attribute_09, env_dict["attribute_09"])
        self.assertEqual(env.attribute_10, env_dict["attribute_10"])


if __name__ == '__main__':
    unittest.main()
