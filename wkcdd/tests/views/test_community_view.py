from webob.multidict import MultiDict
from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.community import CommunityView
from wkcdd.models.community import Community
from wkcdd.models.location import Location
from wkcdd import constants


class TestCommunityView(IntegrationTestBase):
    def setUp(self):
        super(TestCommunityView, self).setUp()
        self.request = testing.DummyRequest()
        self.community_view = CommunityView(self.request)

    def test_show_with_projects_with_no_reports(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Maragoli')
        self.request.context = community
        response = self.community_view.show()
        project_indicator_list = (
            response['aggregated_indicators']['indicator_list'])
        self.assertIsInstance(response['community'], Community)
        self.assertEquals(response['locations']['county'].name, "Bungoma")
        self.assertEquals(project_indicator_list[0]['project_name'],
                          'Dairy Cow Project Center 1')
        self.assertIn('summary', response['aggregated_indicators'])

    def test_show_with_projects_with_reports(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Bukusu')
        self.request.context = community
        response = self.community_view.show()
        project_indicator_list = (
            response['aggregated_indicators']['indicator_list'])
        self.assertIsInstance(response['community'], Community)
        self.assertEquals(response['locations']['county'].name, "Bungoma")
        self.assertEquals(project_indicator_list[0]['project_name'],
                          'Dairy Goat Project Center 1')
        self.assertEquals(project_indicator_list[0]['project_id'], 2)
        self.assertIn('summary', response['aggregated_indicators'])
        self.assertIn(
            response['indicator_mapping'][0]['key'],
            project_indicator_list[0]['indicators'])

    def test_performance_indicator_aggregates_display_without_reports(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Maragoli')
        self.request.context = community
        response = self.community_view.show()
        project_indicator_list = (
            response['aggregated_indicators']['indicator_list'])
        self.assertIsInstance(response['community'], Community)
        self.assertEqual(response['project_types'],
                         constants.PROJECT_REPORT_SECTORS.values())
        self.assertEquals(project_indicator_list[0]['project_name'],
                          'Dairy Cow Project Center 1')


class TestCommunityViewsFunctional(FunctionalTestBase):
    def test_community_show_view(self):
        self.setup_test_data()
        community = Location.get(Location.name == 'Maragoli',
                                 Location.location_type == 'community')
        url = self.request.route_path(
            'community', traverse=(community.id, 'show'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_community_impact_indicator_view(self):
        self.setup_test_data()
        community = Location.get(Location.name == 'Maragoli',
                                 Location.location_type == 'community')
        url = self.request.route_path(
            'community', traverse=(community.id, 'show', 'impact'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_community_performance_indicator_view(self):
        self.setup_test_data()
        community = Location.get(Location.name == 'Maragoli',
                                 Location.location_type == 'community')
        url = self.request.route_path(
            'community', traverse=(community.id, 'show', 'performance'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
