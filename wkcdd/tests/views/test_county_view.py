from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.county import CountyView


class TestCountyView(IntegrationTestBase):
    def setUp(self):
        super(TestCountyView, self).setUp()
        self.request = testing.DummyRequest()
        self.county_view = CountyView(self.request)

    def test_constituency_list_all_projects(self):
        self.setup_test_data()


class TestCommunityViewsFunctional(FunctionalTestBase):
    pass
