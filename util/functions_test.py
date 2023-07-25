import unittest
from util.functions import safe_reduce


class FunctionsTestSuite(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()
