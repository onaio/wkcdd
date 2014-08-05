from pyramid import testing

from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)
from wkcdd.models.user import User
from wkcdd.views.default_views import private


class TestPrivateView(IntegrationTestBase):
    def test_private_view_response(self):
        request = testing.DummyRequest()
        response = private(request)
        self.assertEqual(response.body, "Private view")


class TestHomeViewFunctional(FunctionalTestBase):
    def test_private_view_response(self):
        self._create_user()
        user = User.newest()
        url = self.request.route_url('private')
        auth_headers = self._login_user(user)
        response = self.testapp.get(url, headers=auth_headers)
        self.assertEqual(response.status_code, 200)
