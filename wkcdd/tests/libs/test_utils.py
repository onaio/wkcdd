import unittest

from wkcdd.libs import utils
from wkcdd import constants


class TestUtils(unittest.TestCase):

    def test_humanize_replaces_special_characters(self):
        value = "The_quick-brown*fox@jumped&over$the#moon"
        humanized = utils.humanize(value)
        self.assertEqual(humanized, "The quick brown fox jumped over the moon")

    def test_sum_reduce_func_returns_current_if_none_or_nan(self):
        # value is None
        result = utils.sum_reduce_func('3', None)
        self.assertEqual(result, 3)

        # value is NaN
        result = utils.sum_reduce_func('3', 'a')
        self.assertEqual(result, 3)

    def test_sum_reduce_func_returns_sum_of_value_and_current(self):
        result = utils.sum_reduce_func('2', '3')
        self.assertEqual(result, 5)

    def test_sum_reduce_func_functional(self):
        values = [u'1', u'15', 0, 0, 0, 0]
        result = reduce(utils.sum_reduce_func, values)
        self.assertEqual(result, 16)

    def test_get_performance_indicator_list(self):
        project_sectors = [sector
                           for reg, sector, label
                           in constants.PROJECT_TYPE_MAPPING]
        for sector in project_sectors:
            self.assertIsNotNone(
                utils.get_performance_indicator_list(
                    constants.PERFORMANCE_INDICATORS[sector]))
