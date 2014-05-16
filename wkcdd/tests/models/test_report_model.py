import datetime
import json
import os

from wkcdd import constants
from wkcdd.libs import utils
from wkcdd.models.report import Report
from wkcdd.models.project import Project
from wkcdd.models import County, Constituency, Community
from wkcdd.tests.test_base import TestBase
from wkcdd.models.helpers import get_project_list


class TestReport(TestBase):

    def test_setup_test_data(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == "YH9T")
        json_data = json.load(open(os.path.join(
            self.test_dir, 'fixtures', 'submission_x.json')))
        self.assertEquals(report.report_data, json_data)

    def test_add_report_submission(self):
        self.setup_test_data()
        project_code = 'TG1F'
        constituency = Constituency.get(Constituency.name == "Kakamega")
        community = self._add_community(constituency=constituency)
        project_type = self._add_project_type()
        self._add_project(project_code=project_code, community=community,
                          project_type=project_type)
        report_submission = Report(
            project_code=project_code,
            submission_time=datetime.datetime(2013, 1, 1),
            month=3,
            quarter='q_2',
            period='2013_14',
            report_data="{'data':test}"
        )
        Report.add_report_submission(report_submission)
        report = Report.get(Report.project_code == project_code)

        self.assertEquals(report, report_submission)

    # Number of beneficiaries with increased income earned from the project
    def test_calculate_impact_indicator(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == 'YH9T')
        impact_indicators = report.calculate_impact_indicators()
        self.assertEquals(
            impact_indicators['impact_information/b_income'], '1')
        self.assertEquals(
            impact_indicators['impact_information/b_improved_houses'], '1')
        self.assertEquals(
            impact_indicators['impact_information/b_hh_assets'], '3')
        self.assertEquals(
            impact_indicators['impact_information/no_children'], '3')

    def test_calculate_dairy_cow_performance_indicators(self):
        self.setup_test_data()
        project = Project.get(Project.code == 'YH9T')
        indicators = utils.get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[
                constants.DAIRY_COWS_PROJECT_REPORT])
        criteria = Project.sector == constants.DAIRY_COWS_PROJECT_REGISTRATION
        kwargs = {'project_filter_criteria': criteria}
        rows, summary_row, projects = Report.generate_performance_indicators(
            [project], indicators, **kwargs)

        self.assertIn(project, projects)
        self.assertEquals(
            summary_row['exp_contribution'], 56000)
        self.assertEquals(
            summary_row['actual_contribution'], 96800)
        self.assertEquals(
            summary_row['community_contribution'], 173)
        self.assertEquals(
            summary_row['cws_proceeds_percentage'], 0)
        self.assertEquals(
            summary_row['db_achievement'], 10)
        self.assertEquals(
            summary_row['mb_achievement'], 4)
        self.assertEquals(
            summary_row['fb_achievement'], 6)
        self.assertEquals(
            summary_row['vb_achievement'], 4)
        self.assertEquals(
            summary_row['milk_grp_sale_percentage'], 30)

    def test_calculate_dairy_goat_performance_indicators(self):
        self.setup_test_data()
        project = Project.get(Project.code == 'JDCV')
        indicators = utils.get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[
                constants.DAIRY_GOAT_PROJECT_REPORT])
        criteria = Project.sector == constants.DAIRY_GOAT_PROJECT_REGISTRATION
        kwargs = {'project_filter_criteria': criteria}
        rows, summary_row, projects = Report.generate_performance_indicators(
            [project], indicators, **kwargs)

        self.assertIn(project, projects)
        self.assertEquals(
            summary_row['exp_contribution'], 136275)
        self.assertEquals(
            summary_row['actual_contribution'], 152300)
        self.assertEquals(
            summary_row['community_contribution'], 112)
        self.assertEquals(
            summary_row['bucks_target'], 1)
        self.assertEquals(
            summary_row['bucks_achievement'], 1)
        self.assertEquals(
            summary_row['bucks_percentage'], 100)
        self.assertEquals(
            summary_row['does_proceeds_target'], 7)
        self.assertEquals(
            summary_row['does_proceeds_achievement'], 8)
        self.assertEquals(
            summary_row['does_proceeds_percentage'], 114)
        self.assertEquals(
            summary_row['milk_bnf_sale_percentage'], 0)

    reports = [
        Report(
            report_data={
                'impact_information/b_income': '2060',
                'impact_information/b_improved_houses': '1220',
                # simulate missing report
                # 'impact_information/b_hh_assets':,
                'impact_information/no_children': '1400'
            }
        ),
        Report(
            report_data={
                'impact_information/b_income': '0',
                'impact_information/b_improved_houses': '860',
                'impact_information/b_hh_assets': '230',
                'impact_information/no_children': '670'
            }
        )
    ]

    def test_sum_impact_indicator_values(self):
        indicator_sum = Report.sum_impact_indicator_values(
            'impact_information/b_hh_assets', self.reports)
        self.assertEqual(indicator_sum, 230)

    def test_sum_impact_indicator_values_returns_0_for_list_of_none(self):
        indicator_sum = Report.sum_impact_indicator_values(
            'impact_information/b_hh_assets', [
                Report(report_data={})
            ])
        self.assertEqual(indicator_sum, 0)

    def test_generate_impact_indicators(self):
        self.setup_test_data()
        locations = County.all()
        indicators = utils.get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)
        rows, summary_row = Report.generate_impact_indicators(
            locations, indicators)
        self.assertIsInstance(rows, list)
        self.assertEqual(len(rows), 3)
        self.assertEqual(summary_row['impact_information/b_income'], 20)
        self.assertEqual(
            summary_row['impact_information/b_improved_houses'], 1)
        self.assertEqual(summary_row['impact_information/b_hh_assets'], 3)
        self.assertEqual(summary_row['impact_information/no_children'], 8)

    def test_generate_impact_indicators_for_community_projects(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Maragoli")
        projects = get_project_list([community.id])

        indicators = utils.get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)
        rows, summary_row = Report.generate_impact_indicators(
            projects, indicators)

        self.assertIsInstance(rows, list)
        self.assertEqual(len(rows), 2)
        self.assertEqual(summary_row['impact_information/b_income'], 0)
        self.assertEqual(
            summary_row['impact_information/b_improved_houses'], 0)
        self.assertEqual(summary_row['impact_information/b_hh_assets'], 0)
        self.assertEqual(summary_row['impact_information/no_children'], 0)

    performance_reports = [
        Report(
            report_data={
                'perfomance_summary/exp_contribution': '123',
                'perfomance_summary/actual_contribution': '120',
                'perfomance_summary/community_contribution': '98',
                'mproject_performance/dbirds_number': '15',
                'impact_information/db_percentage': '20'
            }
        ),
        Report(
            report_data={
                'perfomance_summary/exp_contribution': '100',
                'perfomance_summary/actual_contribution': '200',
                'perfomance_summary/community_contribution': '100',
                'mproject_performance/dbirds_number': '30',
                'mproject_performance/db_percentage': '18'
            }
        )
    ]

    def test_sum_performance_indicator_values(self):
        indicator_sum_target = Report.sum_performance_indicator_values(
            'perfomance_summary/exp_contribution',
            'target',
            self.performance_reports)

        indicator_ratio = Report.sum_performance_indicator_values(
            'perfomance_summary/community_contribution',
            'ratio',
            self.performance_reports)

        self.assertEqual(indicator_sum_target, 223)
        self.assertEqual(indicator_ratio, 99)

    def test_sum_performance_indicators_for_legacy_values(self):
        indicator_ratio = Report.sum_performance_indicator_values(
            ['impact_information/db_percentage',
             'mproject_performance/db_percentage'],
            'ratio',
            self.performance_reports)
        self.assertEqual(indicator_ratio, 19)

    def test_generate_performance_indicators(self):
        self.setup_test_data()
        locations = County.all()
        indicators = utils.get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[
                constants.DAIRY_COWS_PROJECT_REPORT])
        criteria = Project.sector == constants.DAIRY_COWS_PROJECT_REGISTRATION
        kwargs = {'project_filter_criteria': criteria}
        rows, summary_row, projects = Report.generate_performance_indicators(
            locations, indicators, **kwargs)
        self.assertEqual(len(rows), 1)

        self.assertEqual(summary_row['exp_contribution'], 680800)
        self.assertEqual(
            summary_row['actual_contribution'], 721600)
        self.assertEqual(
            summary_row['community_contribution'], 45.5)

    def test_generate_performance_indicators_for_legacy_data(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Maragoli")
        indicators = utils.get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[
                constants.DAIRY_COWS_PROJECT_REPORT])
        criteria = Project.sector == constants.DAIRY_COWS_PROJECT_REGISTRATION
        kwargs = {'project_filter_criteria': criteria}
        rows, summary_row, projects = Report.generate_performance_indicators(
            [community], indicators, **kwargs)
        self.assertEqual(len(rows), 1)

        self.assertEquals(
            summary_row['db_achievement'], 13)
        self.assertEquals(
            summary_row['mb_achievement'], 7)
        self.assertEquals(
            summary_row['fb_achievement'], 6)
        self.assertEquals(
            summary_row['vb_achievement'], 3)

    def test_get_reports_for_projects_with_period_and_quarter(self):
        self.setup_report_period_test_data()
        project = Project.get(Project.code == "7CWA")
        period = '2013_14'
        quarter = 'q_4'
        report = Report.get(
            Report.period == period,
            Report.quarter == quarter)

        # Test when quarter is q_4 2013_14
        period_criteria = Report.period == period
        quarter_criteria = Report.quarter == quarter
        criteria = [period_criteria, quarter_criteria]

        reports = Report.get_reports_for_projects([project], *criteria)

        self.assertEqual(len(reports), 1)
        self.assertIn(report, reports)

        # Test when quarter is q_1 2013_14
        quarter = 'q_1'
        period_criteria = Report.period == period
        quarter_criteria = Report.quarter == quarter
        criteria = [period_criteria, quarter_criteria]
        reports = Report.get_reports_for_projects([project], *criteria)

        self.assertEqual(len(reports), 0)

    def test_get_reports_for_projects_with_period_and_year(self):
        self.setup_report_period_test_data()
        project = Project.get(Project.code == "7CWA")
        period = '2013_14'
        month = '8'
        report = Report.get(
            Report.period == period,
            Report.month == month)

        # Test when month is Aug(8) 2013_14

        period_criteria = Report.period == period
        quarter_criteria = Report.month == month
        criteria = [period_criteria, quarter_criteria]

        reports = Report.get_reports_for_projects([project], *criteria)

        self.assertEqual(len(reports), 1)
        self.assertIn(report, reports)

        # Test when month is Jan(1) 2013_14

        month = '1'
        period_criteria = Report.period == period
        quarter_criteria = Report.month == month
        criteria = [period_criteria, quarter_criteria]
        reports = Report.get_reports_for_projects([project], *criteria)
        self.assertEqual(len(reports), 0)

    def test_generate_performance_indicators_with_period(self):
        self.setup_report_period_test_data()
        project = Project.get(Project.code == "7CWA")
        period = '2013_14'
        month = '8'

        period_criteria = Report.period == period
        quarter_criteria = Report.month == month
        period_criteria = [period_criteria, quarter_criteria]

        indicators = utils.get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[
                constants.DAIRY_COWS_PROJECT_REPORT])

        project_sector_criteria = (
            Project.sector == constants.DAIRY_COWS_PROJECT_REGISTRATION)

        kwargs = {'project_filter_criteria': project_sector_criteria,
                  'period_criteria': period_criteria}

        rows, summary_row, projects = Report.generate_performance_indicators(
            [project], indicators, **kwargs)

        self.assertIn(project, projects)
        self.assertEquals(
            summary_row['exp_contribution'], 624800)
        self.assertEquals(
            summary_row['actual_contribution'], 624800)
        self.assertEquals(
            summary_row['community_contribution'], 100)
