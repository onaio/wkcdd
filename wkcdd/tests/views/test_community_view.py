from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.community import CommunityView
from wkcdd.models.community import Community
from wkcdd.models.location import Location


class TestCommunityView(IntegrationTestBase):
    def setUp(self):
        super(TestCommunityView, self).setUp()
        self.request = testing.DummyRequest()
        self.community_view = CommunityView(self.request)

    def test_community_list_all_projects_with_no_reports(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Maragoli')
        self.request.context = community
        response = self.community_view.list_all_projects()
        project_indicator_list = (
            response['aggregated_impact_indicators']['indicator_list'])
        self.assertIsInstance(response['community'], Community)
        self.assertEquals(response['locations']['county'].name, "Bungoma")
        self.assertEquals(project_indicator_list[0]['project_name'],
                          'Dairy Cow Project Center 1')
        self.assertIn('summary', response['aggregated_impact_indicators'])

    def test_community_list_all_with_projects_and_reports(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Bukusu')
        self.request.context = community
        response = self.community_view.list_all_projects()
        project_indicator_list = (
            response['aggregated_impact_indicators']['indicator_list'])
        self.assertIsInstance(response['community'], Community)
        self.assertEquals(response['locations']['county'].name, "Bungoma")
        self.assertEquals(project_indicator_list[0]['project_name'],
                          'Dairy Goat Project Center 1')
        self.assertEquals(project_indicator_list[0]['project_id'], 2)
        self.assertIn('summary', response['aggregated_impact_indicators'])
        self.assertIn(
            response['impact_indicator_mapping'][0]['key'],
            project_indicator_list[0]['indicators'])


class TestCommunityViewsFunctional(FunctionalTestBase):
    def test_community_list_all_projects_view(self):
        self.setup_test_data()
        community = Location.get(Location.name == 'Maragoli')
        url = self.request.route_path('community', traverse=community.id)
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
