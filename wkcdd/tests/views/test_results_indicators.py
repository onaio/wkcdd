from wkcdd.tests.test_base import FunctionalTestBase


class TestResultsIndicators(FunctionalTestBase):
    def test_index_get(self):
        self.setup_test_data()
        url = self.request.route_path('results_indicators', traverse=())
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
