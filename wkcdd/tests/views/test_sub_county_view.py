from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.sub_county import SubCountyView


class TestSubCountyViews(IntegrationTestBase):
    def setUp(self):
        super(TestSubCountyViews, self).setUp()
        self.request = testing.DummyRequest()
        self.sub_county_view = SubCountyView(self.request)

    def test_constituency_list_all_projects(self):
        self.setup_test_data()


class TestCommunityViewsFunctional(FunctionalTestBase):
    pass
