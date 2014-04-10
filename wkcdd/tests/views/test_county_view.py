from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.county import CountyView
from wkcdd.models.county import County
from wkcdd.models.location import Location


class TestCountyViews(IntegrationTestBase):
    def setUp(self):
        super(TestCountyViews, self).setUp()
        self.request = testing.DummyRequest()
        self.county_view = CountyView(self.request)

    def test_show_all_counties(self):
        self.setup_test_data()
        response = self.county_view.show_all_counties()
        self.assertEquals(response['rows'][0][0].name, "Bungoma")
        self.assertEquals(len(response['rows']), 2)
        self.assertEquals(response['summary_row'], [20, 1, 3, 8])

    def test_county_list_all_sub_counties(self):
        self.setup_test_data()
        county = County.get(County.name == "Bungoma")
        self.request.context = county
        response = self.county_view.list_all_sub_counties()
        self.assertEquals(response['rows'][0][0].name, "Bungoma")
        self.assertEquals(len(response['rows']), 1)
        self.assertEquals(response['summary_row'], [16, 1, 3, 8])


class TestCountyViewsFunctional(FunctionalTestBase):
    def test_show_all_counties_view(self):
        self.setup_test_data()
        url = self.request.route_path('counties',  traverse='')
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_county_list_all_sub_counties_view(self):
            self.setup_test_data()
            county = Location.get(Location.name == 'Bungoma',
                                  Location.location_type == 'county')
            url = self.request.route_path('counties', traverse=county.id)
            response = self.testapp.get(url)
            self.assertEqual(response.status_code, 200)

    def test_county_performance_view(self):
        self.setup_test_data()
        county = Location.get(Location.name == 'Bungoma',
                              Location.location_type == 'county')
        url = self.request.route_path('counties', traverse=(
            county.id, 'performance'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
