from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.community import CommunityView
from wkcdd.models.community import Community


class TestCommunityView(IntegrationTestBase):
    def setUp(self):
        super(TestCommunityView, self).setUp()
        self.request = testing.DummyRequest()
        self.community_view = CommunityView(self.request)

    def test_show_projects_with_no_reports(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Maragoli')
        self.request.context = community

        response = self.community_view.show()

        self.assertEquals(response['title'], community.name)
        self.assertEquals(len(response['rows']), len(community.projects))
        self.assertEquals(response['rows'][0][4].name,
                          'Dairy Goat Project Center 1')
        self.assertEquals(response['summary_row'], [0, 0, 0, 0])

    def test_show_projects_with_reports(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Bukusu')
        self.request.context = community

        response = self.community_view.show()
        self.assertEquals(response['title'], community.name)
        self.assertEquals(len(response['rows']), len(community.projects))
        self.assertEquals(response['rows'][0][4].name,
                          'Dairy Cow Project Center 1')
        self.assertEquals(response['rows'][1][4].name,
                          'Dairy Goat Project Center 2')
        self.assertEquals(response['rows'][0][5:], ['1', '1', '3', '3'])
        self.assertEquals(response['rows'][1][5:], ['15', None, None, '5'])
        self.assertEquals(response['summary_row'], [16, 1, 3, 8])

    def test_performance_indicator_aggregates_display_without_reports(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Maragoli')
        self.request.context = community
        response = self.community_view.performance()
        self.assertIsInstance(response['community'], Community)
        self.assertIn('sector_aggregated_indicators', response)
        self.assertIn('project_types', response)


class TestCommunityViewsFunctional(FunctionalTestBase):
    def test_community_show_view(self):
        self.setup_community_test_data()
        community = Community.get(Community.name == 'lutacho')
        url = self.request.route_path(
            'community', traverse=(community.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_community_performance_view(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Maragoli')
        url = self.request.route_path(
            'community', traverse=(community.id, 'performance'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_community_performance_view_with_project_type(self):
        self.setup_community_test_data()
        community = Community.get(Community.name == 'lutacho')
        url = self.request.route_path(
            'community', traverse=(community.id, 'performance'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
