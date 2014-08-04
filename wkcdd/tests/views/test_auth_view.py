from pyramid import testing
from pyramid.httpexceptions import HTTPFound
from webob.multidict import MultiDict

from wkcdd.views.auth import login, logout

from wkcdd.tests.test_base import (
    IntegrationTestBase)


class TestAuth(IntegrationTestBase):
    def test_login(self):
        self._create_admin()
        payload = MultiDict([
            ('username', 'admin'),
            ('password', '****')
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
