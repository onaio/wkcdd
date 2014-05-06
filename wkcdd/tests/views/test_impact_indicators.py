from wkcdd.tests.test_base import FunctionalTestBase
from wkcdd.models import Community


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
