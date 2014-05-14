from wkcdd.tests.test_base import FunctionalTestBase
from wkcdd.models import Community, County, Constituency


class TestImpactIndicatorsFunctional(FunctionalTestBase):

    def test_show_get(self):
        url = self.request.route_path('impact_indicators', traverse=())
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_show_for_community(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Maragoli")
        url = self.request.route_path('impact_indicators',
                                      traverse=(community.id))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_county_projects(self):
        self.setup_test_data()
        county = County.get(County.name == "Bungoma")
        url = self.request.route_path('impact_indicators',
                                      traverse=(county.id),
                                      _query={'view_by': 'projects'})
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_constituency_communities(self):
        self.setup_test_data()
        constituency = Constituency.get(Constituency.name == "Amagoro")
        url = self.request.route_path('impact_indicators',
                                      traverse=(constituency.id))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_all_with_empty_view_by(self):
        self.setup_test_data()
        url = self.request.route_path('impact_indicators',
                                      traverse=(),
                                      _query={'view_by': ''})
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_county_with_empty_view_by(self):
        self.setup_test_data()
        county = County.get(County.name == "Bungoma")
        url = self.request.route_path('impact_indicators',
                                      traverse=(county.id),
                                      _query={'view_by': ''})
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_indicator_filtering_by_month(self):
        self.setup_report_period_test_data()
        county = County.get(County.name == "Bungoma")
        url = self.request.route_path('impact_indicators',
                                      traverse=(county.id),
                                      _query={'month_or_quarter': '1',
                                              'period': '2012_13'})
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_indicator_filtering_by_quarter(self):
        self.setup_report_period_test_data()
        county = County.get(County.name == "Bungoma")
        url = self.request.route_path('impact_indicators',
                                      traverse=(county.id),
                                      _query={'month_or_quarter': 'q_3',
                                              'period': '2013_14'})
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
