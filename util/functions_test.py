import unittest

from parameterized import parameterized

from dashboard.model.deployment import Deployment
from util.functions import safe_reduce, was_deployed, ensure_marker_visibility

deployment_data: dict = {
    'deployment_id': 2099,
    'description': None,
    'location': {'lat': 47.53297706812293, 'lon': 7.61063731466237},
    'node': {'connectivity': 'LoRaWAN',
             'node_id': 17,
             'node_label': '0291-3299',
             'type': 'Env. Sensor'
             },
    'node_id': 17,
    'period': {'end': None, 'start': None},
}


class FunctionsTestSuite(unittest.TestCase):

    # safe_reduce functions tests
    def test_safe_reduce(self):
        result = safe_reduce(lambda x, y: x + y, [0, 1, 2, 3])
        self.assertEqual(result, 6)

    def test_safe_reduce_none_values(self):
        result = safe_reduce(lambda x, y: x + y, [None, 0, None, 1, 2, 3, None])
        self.assertEqual(result, 6)

    def test_safe_reduce_only_none_values(self):
        result = safe_reduce(lambda x, y: x + y, [None, None, None])
        self.assertEqual(result, None)

    def test_safe_reduce_start_value(self):
        result = safe_reduce(lambda x, y: x + y, [0, 1, 2], 10)
        self.assertEqual(result, 13)

    def test_safe_reduce_empty_iterable(self):
        result = safe_reduce(lambda x, y: x + y, [])
        self.assertEqual(result, None)

    # was_deployed function tests
    @parameterized.expand([
        # yyyy-mm-dd
        ("2020-01-03", "2020-01-04", True),   # start and end in range
        ("2020-01-03", "2020-01-11", True),   # only start in range
        ("2019-01-01", "2020-01-04", True),   # only end in range
        ("2019-01-01", "2021-01-01", True),   # start before, end after
        ("2019-01-01", "2020-01-01", False),  # start and end before range
        ("2020-01-11", "2020-01-15", False),  # start and end after range
    ])
    def test_typical_case_was_deployed(self, start, end, expected):
        time_range = ["2020-01-02", "2020-01-10"]
        deployment = Deployment(deployment_data)
        deployment.period_start = start
        deployment.period_end = end

        actual = was_deployed(deployment, time_range[0], time_range[1])
        self.assertEqual(actual, expected)

    def test_typical_case_lat_ensure_marker_visibility(self):
        map_center = [50, 50]
        map_bounds = [[45, 45], [55, 55]]
        marker_position = {"lat": 46, "lon": 50}
        expected = (43.5, 50.0)
        actual = ensure_marker_visibility(map_center, map_bounds, marker_position)
        self.assertEqual(actual, expected)

    def test_typical_case_lon_ensure_marker_visibility(self):
        map_center = [50, 50]
        map_bounds = [[45, 45], [55, 55]]
        marker_position = {"lat": 54, "lon": 46}
        expected = (50.0, 45.0)
        actual = ensure_marker_visibility(map_center, map_bounds, marker_position)
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
