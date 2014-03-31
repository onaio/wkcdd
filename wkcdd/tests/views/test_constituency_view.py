from pyramid import testing
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase
)
from wkcdd.views.constituency import ConstituencyView
from wkcdd.models.constituency import Constituency


class TestConstituencyView(IntegrationTestBase):
    def setUp(self):
        super(TestConstituencyView, self).setUp()
        self.request = testing.DummyRequest()
        self.constituency_view = ConstituencyView(self.request)

    def test_constituency_list_all_communities(self):
        self.setup_test_data()
        constituency = Constituency.get(Constituency.name == "Kakamega")
        self.request.context = constituency
        response = self.constituency_view.list_all_communities()
        self.assertIsInstance(response['constituency'], Constituency)


class TestCommunityViewsFunctional(FunctionalTestBase):
    pass
