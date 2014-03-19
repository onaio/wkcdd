import datetime
from wkcdd.tests.test_base import TestBase
from wkcdd.models.report import Report


class TestReport(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        report = Report.get(Report.project_id == "FR3A")

        self.assertEquals(report.report_data, "{'data':test_report}")

    def test_add_report_submission(self):
        self.setup_test_data()
        report_submission = Report(
            project_id="TGIF",
            report_date=datetime.datetime(2014, 3, 21),
            report_data='[{"test_submission":test}]',
            form_id="dairy_cow_form_report"
        )
        Report.add_report_submission(report_submission)
        report = Report.get(Report.project_id == "TGIF")

        self.assertEquals(report, report_submission)