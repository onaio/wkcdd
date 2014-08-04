from pyramid import testing
from pyramid.httpexceptions import HTTPFound
from webob.multidict import MultiDict

from wkcdd.security import pwd_context
from wkcdd.models.base import DBSession
from wkcdd.models.user import User, ADMIN_PERM
from wkcdd.views.auth import login, logout

from wkcdd.tests.test_base import (
    IntegrationTestBase)


class TestAuth(IntegrationTestBase):

    def _create_user(self):
        # create the user
        user = User(
            username="admin",
            pwd=pwd_context.encrypt("admin"),
            active=True,
            group=ADMIN_PERM)
        DBSession.add(user)

    def test_login(self):
        self._create_user()
        payload = MultiDict([
            ('username', 'admin'),
            ('password', 'admin')
        ])
        request = testing.DummyRequest(post=payload)
        response = login(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, request.route_url(
            'reports', traverse=()))

    def test_bad_login(self):
        self._create_user()
        payload = MultiDict([
            ('username', 'admin'),
            ('password', 'bad_admin')
        ])
        request = testing.DummyRequest(post=payload)
        response = login(request)
        flash_message = request.session.values()[0][0]
        self.assertEqual(flash_message, u"Invalid username or password")
        self.assertEqual(response, {})

    def test_logout(self):
        request = testing.DummyRequest()
        response = logout(request)
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(
            response.location,
            request.route_url('performance_indicators', traverse=()))
