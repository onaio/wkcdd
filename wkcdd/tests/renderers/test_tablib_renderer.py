import unittest

from pyramid import testing
from wkcdd.tests.test_base import IntegrationTestBase
from wkcdd.renderers import TablibXLSXRenderer
from wkcdd.libs.utils import get_impact_indicator_list
from wkcdd.views.helpers import get_performance_sector_mapping
from wkcdd import constants
from wkcdd.models import County
from wkcdd.models import Project, Report


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

    def test_renderer_output_for_performance_indicators(self):
        request = testing.DummyRequest()
        renderer = TablibXLSXRenderer({})
        sectors = get_performance_sector_mapping()
        goat_reg_id = constants.DAIRY_GOAT_PROJECT_REGISTRATION
        goat_sector_data = {'rows': [
            {'indicators': {
                            'exp_contribution': 0,
                            'actual_contribution': 0,
                            'community_contribution': 0,
                            'bucks_target': 0,
                            'bucks_achievement': 0,
                            'bucks_percentage': 0},
             'location': County(name="bla", id=1)
             }],
            'summary_row': {'exp_contribution': 0,
                            'actual_contribution': 0,
                            'community_contribution': 0,
                            'bucks_target': 0,
                            'bucks_achievement': 0,
                            'bucks_percentage': 0}}
        data = {
            'sectors': sectors,
            'is_impact': False,
            'sector_indicators': {
                goat_reg_id: (
                    ('Community Contribution', (
                        'exp_contribution',
                        'actual_contribution',
                        'community_contribution')),
                    ('Local Bucks Acquired', (
                        'bucks_target',
                        'bucks_achievement',
                        'bucks_percentage')))
            },
            'sector_data': {
                goat_reg_id: goat_sector_data},
            'search_criteria': {'selected_sector': {'sector': goat_reg_id}}
        }
        renderer(data, {'request': request})
        self.assertEqual(
            request.response.content_type,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # noqa


class TestTablibRendererIntegration(IntegrationTestBase):
    def test_generate_project_mis_export(self):
        self.setup_test_data()
        projects = Project.all()
        request = testing.DummyRequest()
        renderer = TablibXLSXRenderer({})
        data = {'projects': projects,
                'is_project_export': True}

        renderer(data, {'request': request})
        self.assertEqual(
            request.response.content_type,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # noqa

    def test_generate_project_report_mis_export(self):
        self.setup_report_period_test_data()
        reports = Report.all()
        request = testing.DummyRequest()
        renderer = TablibXLSXRenderer({})
        data = {'reports': reports,
                'is_report_export': True}
        renderer(data, {'request': request})

        self.assertEqual(
            request.response.content_type,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # noqa
