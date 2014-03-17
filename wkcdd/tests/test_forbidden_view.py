from wkcdd.tests.test_base import (
    TestBase,
    IntegrationTestBase,
    FunctionalTestBase)


class TestForbiddenViewFunctional(FunctionalTestBase):
    def test_render_login_when_forbidden_and_not_authenticated(self):
        url = self.request.route_url('private')
        response = self.testapp.get(url, status=401)
        self.assertEqual(response.status_code, 401)
        response.mustcontain('Login')

    def test_render_unauthorized_when_forbidden_and_authenticated(self):
        url = self.request.route_url('supervisors_only')
        headers = self._login_user(3)
        response = self.testapp.get(url, headers=headers, status=403)
        self.assertEqual(response.status_code, 403)