from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.constituency import ConstituencyView
from wkcdd.models.constituency import Constituency
from wkcdd.models.location import Location


class TestConstituencyView(IntegrationTestBase):
    def setUp(self):
        super(TestConstituencyView, self).setUp()
        self.request = testing.DummyRequest()
        self.constituency_view = ConstituencyView(self.request)

    def test_constituency_list_all_communities(self):
        self.setup_test_data()
        constituency = Constituency.get(Constituency.name == "Kakamega")
        self.request.context = constituency
        response = self.constituency_view.list_all_communities()
        self.assertEquals(len(response['rows']), 2)
        self.assertEquals(response['summary_row'], [16, 1, 3, 8])


class TestConstituencyViewsFunctional(FunctionalTestBase):
    def test_constituency_list_all_communities_view(self):
        self.setup_test_data()
        constituency = Location.get(Location.name == 'Kakamega',
                                    Location.location_type == 'constituency')
        url = self.request.route_path('constituency', traverse=constituency.id)
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
