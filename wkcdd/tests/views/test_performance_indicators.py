from wkcdd.tests.test_base import FunctionalTestBase


class TestPerformanceIndicatorsFunctional(FunctionalTestBase):

    def test_index_get(self):
        self.setup_test_data()
        url = self.request.route_path('performance_indicators', traverse=())
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
