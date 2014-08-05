from pyramid import testing
from pyramid.httpexceptions import HTTPFound
from webob.multidict import MultiDict

from wkcdd.models.user import User, CPC_PERM
from wkcdd.views.users import AdminView
from wkcdd.views.user_form import UserForm

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

    def test_add_user(self):
        self._create_admin()
        admin = User.get(User.username == "admin")
        self.request.context = admin
        params = MultiDict([
            ('username', 'test_1'),
            ('__start__', 'password:mapping'),
            ('password', '123456'),
            ('password-confirm', '123456'),
            ('__end__', 'password:mapping'),
            ('active', True),
            ('group', CPC_PERM)])
        self.request.method = "POST"
        self.request.POST = params
        user_count = User.count()

        response = self.views.add_user()
        self.assertIsInstance(response, HTTPFound)

        new_user_count = User.count()
        self.assertEqual(new_user_count, user_count + 1)

    def test_add_user_fails_with_invalid_input(self):
        self._create_admin()
        admin = User.get(User.username == "admin")
        self.request.context = admin
        params = MultiDict([
            ('username', 'test_1'),
            ('__start__', 'password:mapping'),
            ('password', 'bla'),
            ('password-confirm', 'bla'),
            ('__end__', 'password:mapping'),
            ('active', True),
            ('group', CPC_PERM)])
        self.request.method = "POST"
        self.request.POST = params

        response = self.views.add_user()

        self.assertIsInstance(response['form'].schema, UserForm)

        flash_message = self.request.session.values()[0][0]
        self.assertEqual(
            flash_message, "Please fix the errors indicated below.")


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
