import unittest

from wkcdd.libs import utils


class TestUtils(unittest.TestCase):
    def test_humanize_replaces_special_characters(self):
        value = "The_quick-brown*fox@jumped&over$the#moon"
        humanized = utils.humanize(value)
        self.assertEqual(humanized, "The quick brown fox jumped over the moon")