import os

from pyramid import testing
from wkcdd.tests.test_base import (
    _load_json_fixture,
    IntegrationTestBase,
    FunctionalTestBase)

from wkcdd.models.report import (
    Report
)

from wkcdd.views.reports import ReportViews


class TestReportViews(IntegrationTestBase):

    def setUp(self):
        super(TestReportViews, self).setUp()
        self.request = testing.DummyRequest()
        self.report_views = ReportViews(self.request)

    def post_json(self, payload=None):
        request = testing.DummyRequest()
        if payload:
            request.body = payload
        report_views = ReportViews(request)
        return report_views.json_post()

    def test_list_report_returns_all_pending_projects(self):
        self.setup_test_data()
        report = Report.get(Report.status == Report.PENDING)
        response = self.report_views.list()
        self.assertEqual(response['reports'], [report])

    def test_json_post(self):
        count = Report.count()
        report_data_1 = _load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', 'YH9T.json'))
        response = self.post_json(report_data_1)

        self.assertEqual(Report.count(), (count + 1))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.body, 'Saved')


class TestReportViewsFunctional(FunctionalTestBase):

    def test_report_submission_list(self):
        self.setup_test_data()
        url = self.request.route_path('reports', traverse=())
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_report_submission_approval(self):
        self.setup_test_data()
        report = Report.get(Report.status == Report.PENDING)
        url = self.request.route_path(
            'reports',
            traverse=('update'))
        response = self.testapp.post(
            url,
            params={'reports': '{},'.format(report.id)})
        self.assertEqual(response.status_code, 302)
