from pyramid import testing
# from pyramid.httpexceptions import HTTPFound
# from webob.multidict import MultiDict

from wkcdd.models.user import User
from wkcdd.views.users import AdminView

from wkcdd.tests.test_base import (
    IntegrationTestBase, FunctionalTestBase)


class TestUsersView(IntegrationTestBase):
    def setUp(self):
        super(TestUsersView, self).setUp()
        self.request = testing.DummyRequest()
        self.views = AdminView(self.request)

    def test_list_users(self):
        self._create_admin()
        admin = User.get(User.username == "admin")
        self.request.context = admin
        response = self.views.list()
        self.assertEqual(len(response['users']), 1)


class TestUsersViewFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestUsersViewFunctional, self).setUp()
        self._create_admin()
        self.admin = User.get(User.username == "admin")

    def test_list_view(self):
        url = self.request.route_path('users', traverse=())
        headers = self._login_user(self.admin)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
