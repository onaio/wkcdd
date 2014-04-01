from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.sub_county import SubCountyView
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.location import Location


class TestSubCountyViews(IntegrationTestBase):
    def setUp(self):
        super(TestSubCountyViews, self).setUp()
        self.request = testing.DummyRequest()
        self.sub_county_view = SubCountyView(self.request)

    def test_sub_county_list_all_constituencies(self):
        self.setup_test_data()
        sub_county = SubCounty.get(SubCounty.name == "Bungoma")
        self.request.context = sub_county
        response = self.sub_county_view.list_all_constituencies()
        self.assertIsInstance(response['sub_county'], SubCounty)
        self.assertEquals(response['constituencies'][0].name, "Kakamega")
        self.assertEquals(response['locations']['county'].name, "Bungoma")


class TestSubCountyViewsFunctional(FunctionalTestBase):
        def test_sub_county_list_all_constituencies_view(self):
            self.setup_test_data()
            sub_county = Location.get(Location.name == 'Bungoma',
                                      Location.location_type == 'sub_county')
            url = self.request.route_path('sub_county', traverse=sub_county.id)
            response = self.testapp.get(url)
            self.assertEqual(response.status_code, 200)
