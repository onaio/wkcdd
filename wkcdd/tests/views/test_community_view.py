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

        self.assertEquals(response['title'], community.name)
        self.assertEquals(len(response['rows']), len(community.projects))
        self.assertEquals(response['rows'][0][0].name,
                          'Dairy Cow Project Center 1')
        self.assertEquals(response['summary_row'], [0, 0, 0, 0])

    def test_community_list_all_with_projects_and_reports(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Bukusu')
        self.request.context = community
        response = self.community_view.list_all_projects()
        self.assertEquals(response['title'], community.name)
        self.assertEquals(len(response['rows']), len(community.projects))
        self.assertEquals(response['rows'][0][0].name,
                          'Dairy Goat Project Center 1')
        self.assertEquals(response['rows'][1][0].name,
                          'Dairy Goat Project Center 2')
        self.assertEquals(response['rows'][0][1:], ['1', '1', '3', '3'])
        self.assertEquals(response['rows'][1][1:], ['15', None, None, '5'])
        self.assertEquals(response['summary_row'], [16, 1, 3, 8])


class TestCommunityViewsFunctional(FunctionalTestBase):
    def test_community_list_all_projects_view(self):
        self.setup_test_data()
        community = Location.get(Location.name == 'Maragoli',
                                 Location.location_type == 'community')
        url = self.request.route_path('community', traverse=community.id)
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
