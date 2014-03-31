from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.constituency import ConstituencyView


class TestConstituencyView(IntegrationTestBase):
    def setUp(self):
        super(TestConstituencyView, self).setUp()
        self.request = testing.DummyRequest()
        self.constituency_view = ConstituencyView(self.request)

    def test_constituency_list_all_projects(self):
        self.setup_test_data()


class TestCommunityViewsFunctional(FunctionalTestBase):
    pass
