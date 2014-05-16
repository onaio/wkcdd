from wkcdd.tests.test_base import FunctionalTestBase
from wkcdd.models import Constituency


class TestPerformanceIndicatorsFunctional(FunctionalTestBase):

    def test_index_get(self):
        self.setup_test_data()
        url = self.request.route_path('performance_indicators', traverse=())
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_show_constituency(self):
        self.setup_test_data()
        constituency = Constituency.get(Constituency.name == "Kakamega")
        url = self.request.route_path('performance_indicators',
                                      traverse=(constituency.id))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
