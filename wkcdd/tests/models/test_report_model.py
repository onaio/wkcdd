import datetime
from wkcdd.tests.test_base import TestBase
from wkcdd.models.report import Report


class TestReport(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == "YH9T")

        self.assertEquals(report.report_data, "{'data':test}")

    def test_add_report_submission(self):
        self.setup_test_data()
        report_submission = Report(
            project_code="TGIF",
            submission_time=datetime.datetime(2013, 1, 1),
            month=3,
            quarter='q_2',
            period='2013_14',
            report_data="{'data':test}"
        )
        Report.add_report_submission(report_submission)
        report = Report.get(Report.project_code == "TGIF")

        self.assertEquals(report, report_submission)

    # Number of beneficiaries with increased income earned from the project
    def test_calculate_impact_indicator(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == 'YH9T')
        impact_indicators = report.calculate_impact_indicators()
        self.assertEquals(impact_indicators['no_of_b_increased_income'],
                     2)
        self.assertEquals(impact_indicators['no_of_b_improved_houses'],
                     3)
        self.assertEquals(impact_indicators['no_of_b_hh_assets'],
                     4)
        self.assertEquals(impact_indicators['no_of_children'],
                     5)
