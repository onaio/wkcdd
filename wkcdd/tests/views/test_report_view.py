import os
import datetime

from pyramid import testing

from webob.multidict import MultiDict
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)

from wkcdd.models.report import (
    Report
)

from wkcdd.models.meeting import MeetingReport, SaicMeetingReport

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
        report_data = open(os.path.join(
            self.test_dir, 'fixtures', 'YH9T.json'), 'r').read()
        response = self.post_json(report_data)

        self.assertEqual(Report.count(), (count + 1))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.body, 'Saved')

    def test_json_post_for_saic_meeting_report(self):
        count = SaicMeetingReport.count()
        report_data = open(os.path.join(
            self.test_dir, 'fixtures', 'SAIC_REPORT.json'), 'r').read()
        response = self.post_json(report_data)

        self.assertEqual(SaicMeetingReport.count(), (count + 1))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.body, 'Saved')

    def test_json_post_for_meeting_report(self):
        count = MeetingReport.count()
        report_data = open(os.path.join(
            self.test_dir, 'fixtures', 'MEETING_REPORT.json'), 'r').read()
        response = self.post_json(report_data)

        self.assertEqual(MeetingReport.count(), (count + 1))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.body, 'Saved')

    def test_json_post_with_bad_json(self):
        count = Report.count()
        report_data = '{"data":"bad json"}'
        response = self.post_json(report_data)

        self.assertEqual(Report.count(), count)
        self.assertEqual(response.status_code, 202)

    def test_report_submission_approval(self):
        report = Report(
            project_code='abc',
            submission_time=datetime.datetime.now(),
            month=1,
            quarter='q_2',
            period='2013_14',
            report_data="{'data':'bla'}")
        report.save()
        params = MultiDict(
            {'new_status': 'approved',
             'reports': '{}'.format(report.id)})
        self.request.POST = params
        response = self.report_views.update()
        self.assertEqual(response.status_code, 302)


class TestReportViewsFunctional(FunctionalTestBase):

    def test_report_submission_list(self):
        self.setup_test_data()
        url = self.request.route_path('reports', traverse=())
        response = self.testapp.get(url, status=401)
        self.assertEqual(response.status_code, 401)
        response.mustcontain('<title>Login')
