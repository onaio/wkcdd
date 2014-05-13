import unittest

from pyramid import testing
from wkcdd.renderers import TablibXLSXRenderer
from wkcdd.libs.utils import get_impact_indicator_list
from wkcdd import constants
from wkcdd.models import County


class TestTablibRenderer(unittest.TestCase):

    def test_renderer_output(self):
        request = testing.DummyRequest()
        renderer = TablibXLSXRenderer({})
        indicators = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)
        data = {
            'indicators': indicators,
            'is_impact': True,
            'rows': [
                {'indicators': {
                    'impact_information/no_children': 0,
                    'impact_information/b_improved_houses': 0,
                    'impact_information/b_hh_assets': 0,
                    'impact_information/b_income': 0},
                 'location': County(name="bla", id=1)
                 }],
            'summary_row': {'impact_information/no_children': 0,
                            'impact_information/b_improved_houses': 0,
                            'impact_information/b_hh_assets': 0,
                            'impact_information/b_income': 0}
        }
        renderer(data, {'request': request})
        self.assertEqual(
            request.response.content_type,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # noqa
