import unittest
from validations import cleanup_timeseries


class ValidationTestSuite(unittest.TestCase):

    def test_empty_series(self):
        test_dict = {"time": [], "value": []}
        result = cleanup_timeseries(test_dict, 0, 10)
        self.assertEqual(test_dict, result)

    def test_typical_case(self):
        test_dict = {"time": [0, 1, 2, 3, 4], "value": [4, 5, 6, 7, 8]}
        result = cleanup_timeseries(test_dict, 0, 10)
        self.assertEqual(test_dict, result)

    def test_upper_boundary(self):
        test_dict = {"time": [0, 1, 2, 3, 4], "value": [4, 5, 11, 7, 8]}
        result = cleanup_timeseries(test_dict, 0, 10)
        self.assertEqual({"time": [0, 1, 3, 4], "value": [4, 5, 7, 8]}, result)

    def test_lower_boundary(self):
        test_dict = {"time": [0, 1, 2, 3, 4], "value": [4, 5, 6, 7, -8]}
        result = cleanup_timeseries(test_dict, 0, 10)
        self.assertEqual({"time": [0, 1, 2, 3], "value": [4, 5, 6, 7]}, result)

    def test_custom_keys(self):
        test_dict = {"value1": [0, 1, 2, 3, 4], "value2": [4, 15, 6, 7, -8]}
        result = cleanup_timeseries(test_dict, 0, 10, "value1", "value2")
        self.assertEqual({"value1": [0, 2, 3], "value2": [4, 6, 7]}, result)


if __name__ == '__main__':
    unittest.main()
