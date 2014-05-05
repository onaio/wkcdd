from wkcdd.tests.test_base import FunctionalTestBase


class TestImpactIndicatorsFunctional(FunctionalTestBase):
    def test_show_get(self):
        url = self.request.route_path('impact_indicators', traverse=())
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)