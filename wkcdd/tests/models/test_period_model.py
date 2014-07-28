from wkcdd.models.period import Period
from wkcdd.tests.test_base import TestBase


class TestPeriod(TestBase):
    def test_latest_quarter(self):
        self.setup_test_data()
        latest_period = Period.latest_quarter()
        self.assertEqual(latest_period.quarter, 'q_2')
        self.assertEqual(latest_period.year, '2013_14')
