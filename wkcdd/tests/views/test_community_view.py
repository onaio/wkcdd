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

    def test_community_list_all_projects(self):
        self.setup_test_data()
        community = Community.get(Community.name == 'Maragoli')
        self.request.context = community
        response = self.community_view.list_all_projects()
        self.assertIsInstance(response['community'], Community)
        self.assertEquals(response['projects'][0].code, "FR3A")
        self.assertEquals(response['locations']['county'].name, "Bungoma")


class TestCommunityViewsFunctional(FunctionalTestBase):
    def test_community_list_all_projects_view(self):
        self.setup_test_data()
        community = Location.get(Location.name == 'Maragoli',
                                 Location.location_type == 'community')
        url = self.request.route_path('community', traverse=community.id)
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
