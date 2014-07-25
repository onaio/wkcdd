import datetime
import json
import os

from wkcdd import constants
from wkcdd.libs import utils
from wkcdd.models.indicator import (
    TotalAverageMonthlyIncomeIndicator,
    TotalDirectBeneficiariesIndicator,
    PercentageIncomeIncreasedIndicator,
    TotalBeneficiariesIndicator,
    TotalFemaleBeneficiariesIndicator,
    TotalVulnerableCIGMemberIndicator,
    TotalCIGMemberIndicator,
    ExpectedCGAAttendanceIndicator,
    ActualCGAAttendanceIndicator,
    PercentageCGAAttendanceIndicator,
    ExpectedCDDCAttendanceIndicator,
    ActualCDDCAttendanceIndicator,
    PercentageCDDCAttendanceIndicator,
    ExpectedPMCAttendanceIndicator,
    ActualPMCAttendanceIndicator,
    PercentagePMCAttendanceIndicator,
    ExpectedCIGAttendanceIndicator,
    ActualCIGAttendanceIndicator,
    PercentageCIGAttendanceIndicator,
    CDDCManagemnentCountIndicator,
    ProjectMappingIndicator,
    FinancialInformationIndicator)
from wkcdd.models.report import Report
from wkcdd.models.period import Period
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
        rows, summary_row = Report.generate_performance_indicators(
            [project], indicators, **kwargs)

        self.assertEquals(
            summary_row['exp_contribution'], 56000)
        self.assertEquals(
            summary_row['actual_contribution'], 96800)
        self.assertEquals(
            summary_row['community_contribution'], 172.86)
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
            summary_row['milk_grp_sale_percentage'], 29.63)

    def test_calculate_dairy_goat_performance_indicators(self):
        self.setup_test_data()
        project = Project.get(Project.code == 'JDCV')
        indicators = utils.get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[
                constants.DAIRY_GOAT_PROJECT_REPORT])
        criteria = Project.sector == constants.DAIRY_GOAT_PROJECT_REGISTRATION
        kwargs = {'project_filter_criteria': criteria}
        rows, summary_row = Report.generate_performance_indicators(
            [project], indicators, **kwargs)

        self.assertEquals(
            summary_row['exp_contribution'], 136275)
        self.assertEquals(
            summary_row['actual_contribution'], 152300)
        self.assertEquals(
            summary_row['community_contribution'], 111.76)
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
            summary_row['does_proceeds_percentage'], 114.29)
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
        # pending reports are not included in the calculation of this sum

        self.assertEqual(summary_row['impact_information/b_income'], 16)
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
                'impact_information/mb_target': '20'
            }
        ),
        Report(
            report_data={
                'perfomance_summary/exp_contribution': '100',
                'perfomance_summary/actual_contribution': '200',
                'perfomance_summary/community_contribution': '100',
                'mproject_performance/dbirds_number': '30',
                'mproject_performance/mb_target': '18'
            }
        )
    ]

    def test_sum_performance_indicator_values(self):
        indicator_sum_target = Report.sum_performance_indicator_values(
            'perfomance_summary/exp_contribution',
            self.performance_reports)

        self.assertEqual(indicator_sum_target, 223)

    def test_sum_performance_indicators_for_legacy_values(self):
        indicator_ratio = Report.sum_performance_indicator_values(
            ['impact_information/mb_target',
             'mproject_performance/mb_target'],
            self.performance_reports)
        self.assertEqual(indicator_ratio, 38)

    def test_generate_performance_indicators(self):
        self.setup_test_data()
        locations = County.all()
        indicators = utils.get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[
                constants.DAIRY_COWS_PROJECT_REPORT])
        criteria = Project.sector == constants.DAIRY_COWS_PROJECT_REGISTRATION
        kwargs = {'project_filter_criteria': criteria}
        rows, summary_row = Report.generate_performance_indicators(
            locations, indicators, **kwargs)
        self.assertEqual(len(rows), 1)

        self.assertEqual(summary_row['exp_contribution'], 680800)
        self.assertEqual(
            summary_row['actual_contribution'], 721600)
        self.assertEqual(
            summary_row['community_contribution'], 105.99)

    def test_generate_performance_indicators_for_legacy_data(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Maragoli")
        indicators = utils.get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[
                constants.DAIRY_COWS_PROJECT_REPORT])
        criteria = Project.sector == constants.DAIRY_COWS_PROJECT_REGISTRATION
        kwargs = {'project_filter_criteria': criteria}
        rows, summary_row = Report.generate_performance_indicators(
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

        reports = Report.get_reports_for_projects([project.id], *criteria)

        self.assertEqual(len(reports), 1)
        self.assertIn(report, reports)

        # Test when quarter is q_1 2013_14
        quarter = 'q_1'
        period_criteria = Report.period == period
        quarter_criteria = Report.quarter == quarter
        criteria = [period_criteria, quarter_criteria]
        reports = Report.get_reports_for_projects([project.id], *criteria)

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

        reports = Report.get_reports_for_projects([project.id], *criteria)

        self.assertEqual(len(reports), 1)
        self.assertIn(report, reports)

        # Test when month is Jan(1) 2013_14

        month = '1'
        period_criteria = Report.period == period
        quarter_criteria = Report.month == month
        criteria = [period_criteria, quarter_criteria]
        reports = Report.get_reports_for_projects([project.id], *criteria)
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

        rows, summary_row = Report.generate_performance_indicators(
            [project], indicators, **kwargs)

        self.assertEquals(
            summary_row['exp_contribution'], 624800)
        self.assertEquals(
            summary_row['actual_contribution'], 624800)
        self.assertEquals(
            summary_row['community_contribution'], 100)

    def test_get_periods_for_impact_indicators(self):
        self.setup_test_data()
        locations = County.all()
        periods = Report.get_periods_for(locations)

        self.assertEqual(periods['months'], set([3]))
        self.assertEqual(periods['years'], set(['2013_14']))
        self.assertEqual(periods['quarters'], set(['q_2']))

    def test_get_periods_for_performance_indicators(self):
        self.setup_report_period_test_data()
        locations = County.all()

        # test with preset sector
        project_sector_criteria = (
            Project.sector == constants.DAIRY_COWS_PROJECT_REGISTRATION)
        periods = Report.get_periods_for(locations, project_sector_criteria)

        self.assertEqual(periods['months'], set([1, 5, 8, 12]))
        self.assertEqual(periods['years'], set(['2012_13', '2013_14']))
        self.assertEqual(periods['quarters'],
                         set(['q_1', 'q_2', 'q_3', 'q_4']))

    def test_get_periods_without_sector_reports(self):
        self.setup_report_period_test_data()
        locations = County.all()

        # test with preset sector
        project_sector_criteria = (
            Project.sector == constants.DAIRY_GOAT_PROJECT_REGISTRATION)
        periods = Report.get_periods_for(locations, project_sector_criteria)

        self.assertFalse(periods['months'])
        self.assertFalse(periods['years'])
        self.assertFalse(periods['quarters'])

    def test_get_trend_values_for_impact_indicators(self):
        self.setup_report_trends_data()
        locations = County.all()

        time_criteria = [Report.month == 2,
                         Report.period == '2012_13']
        time_criteria = Report.period == '2012_13'
        period_label = 'February, 2012'
        indicators = utils.get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)

        data = Report.get_trend_values_for_impact_indicators(
            locations, indicators, period_label, time_criteria)
        self.assertIn(locations[0].pretty, data)

    def test_month_interval(self):
        self.setup_report_trends_data()
        start_month = '1'
        end_month = '12'
        months = Report.get_month_interval(
            start_month, end_month, '2012_13', '2012_13')
        self.assertEqual([m for m, y in months], [1, 5])

    def test_quarter_interval(self):
        self.setup_report_trends_data()
        start_quarter = 'q_2'
        end_quarter = 'q_4'
        quarters = Report.get_quarter_interval(
            start_quarter, end_quarter, '2012_13', '2012_13')
        self.assertEqual([q for q, y in quarters], ['q_2'])

    def test_get_trend_values_for_performance_indicators(self):
        self.setup_report_trends_data()
        location = County.get(County.name == 'Bungoma')

        time_criteria = [Report.month == '1',
                         Report.period == '2012_13']
        project_filter_criteria = Project.sector == (
            constants.DAIRY_COWS_PROJECT_REGISTRATION)

        indicators = utils.get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[
                constants.DAIRY_COWS_PROJECT_REPORT])

        period_label = 'February, 2012'
        kwargs = {'project_filter_criteria': project_filter_criteria,
                  'time_criteria': time_criteria}

        data = Report.get_trend_values_for_performance_indicators(
            [location], indicators, period_label, **kwargs)

        self.assertIn(location.pretty, data)

    def test_get_latest_month_available(self):
        self.setup_report_trends_data()
        results = Report.get_latest_month_for_year('2012_13')

        self.assertEqual(results[0], 5)

    def _result_indicator_setup(self):
        self.setup_test_data()
        locations = County.all()
        project_ids = []

        for location in locations:
            project_ids.extend(location.get_project_ids())

        self.project_ids = project_ids
        self.period = Period('q_2', '2013_14')

    def test_calculation_of_percentage_income_increased(self):
        self._result_indicator_setup()

        percentage_income_increased = \
            PercentageIncomeIncreasedIndicator.get_value(
                self.project_ids,
                self.period)

        self.assertAlmostEqual(percentage_income_increased, 330.88235294117646)

    def test_calculation_of_total_beneficiaries(self):
        self._result_indicator_setup()
        total_beneficiaries = \
            TotalBeneficiariesIndicator.get_value(
                self.project_ids, self.period)

        self.assertAlmostEqual(percentage_income_increased, 330.88235294117646)

    def test_total_direct_beneficiaries_indicator(self):
        self._result_indicator_setup()
        total_beneficiaries = \
            TotalDirectBeneficiariesIndicator.get_value(self.project_ids)
        self.assertEqual(total_beneficiaries, 34)

    def test_average_monthly_income_indicator(self):
        self._result_indicator_setup()
        total_beneficiaries = \
            TotalAverageMonthlyIncomeIndicator.get_value(self.project_ids)
        self.assertEqual(total_beneficiaries, 11250.0)

    def test_total_female_beneficiaries_indicator(self):
        self._result_indicator_setup()
        total_female_beneficiaries = \
            TotalFemaleBeneficiariesIndicator.get_value(self.project_ids)
        self.assertEqual(total_female_beneficiaries, 20.0)

    def test_total_vulnerable_members_indicator(self):
        self._result_indicator_setup()
        total_vulnerable_members = \
            TotalVulnerableCIGMemberIndicator.get_value(self.project_ids)

        self.assertEqual(total_vulnerable_members, 67.0)

    def test_total_cig_member_indicator(self):
        self._result_indicator_setup()
        total_cig_members = TotalCIGMemberIndicator.get_value(self.project_ids)
        self.assertEqual(total_cig_members, 276.0)

    def test_expected_cig_cga_attendance_indicator(self):
        self._result_indicator_setup()
        expected_cga_attendance = \
            ExpectedCGAAttendanceIndicator.get_value('q_2')
        self.assertEqual(expected_cga_attendance, 104.0)

    def test_actual_cig_cga_attendance_indicator(self):
        self._result_indicator_setup()
        actual_cga_attendance = \
            ActualCGAAttendanceIndicator.get_value('q_2')
        self.assertEqual(actual_cga_attendance, 93.0)

    def test_percentage_cga_attendcance_indicator(self):
        self._result_indicator_setup()
        percentage_cga_attendance = \
            PercentageCGAAttendanceIndicator.get_value('q_2')
        self.assertAlmostEqual(percentage_cga_attendance, 1.118279569892473)

    def test_expected_cddc_attendance_indicator(self):
        self._result_indicator_setup()
        expected_cddc_attendance = \
            ExpectedCDDCAttendanceIndicator.get_value('q_2')
        self.assertEqual(expected_cddc_attendance, 15.0)

    def test_actual_cddc_attendance_indicator(self):
        self._result_indicator_setup()
        actual_cddc_attendance = \
            ActualCDDCAttendanceIndicator.get_value('q_2')
        self.assertEqual(actual_cddc_attendance, 12.0)

    def test_percentage_cddc_attendcance_indicator(self):
        self._result_indicator_setup()
        percentage_cddc_attendance = \
            PercentageCDDCAttendanceIndicator.get_value('q_2')
        self.assertAlmostEqual(percentage_cddc_attendance, 1.25)

    def test_expected_pmc_attendance_indicator(self):
        self._result_indicator_setup()
        expected_pmc_attendance = \
            ExpectedPMCAttendanceIndicator.get_value(self.project_ids)
        self.assertEqual(expected_pmc_attendance, 30.0)

    def test_actual_pmc_attendance_indicator(self):
        self._result_indicator_setup()
        actual_pmc_attendance = \
            ActualPMCAttendanceIndicator.get_value(self.project_ids)
        self.assertEqual(actual_pmc_attendance, 27.0)

    def test_percentage_pmc_attendance_indicator(self):
        self._result_indicator_setup()
        percentage_pmc_attendance = \
            PercentagePMCAttendanceIndicator.get_value(self.project_ids)
        self.assertEqual(percentage_pmc_attendance, 1.1111111111111112)

    def test_expected_cig_attendance_indicator(self):
        self._result_indicator_setup()
        expected_cig_attendance = \
            ExpectedCIGAttendanceIndicator.get_value(self.project_ids)
        self.assertEqual(expected_cig_attendance, 277.0)

    def test_actual_cig_attendance_indicator(self):
        self._result_indicator_setup()
        actual_cig_attendance = \
            ActualCIGAttendanceIndicator.get_value(self.project_ids)
        self.assertEqual(actual_cig_attendance, 157.0)

    def test_percentage_cig_attendance_indicator(self):
        self._result_indicator_setup()
        percentage_cig_attendance = \
            PercentageCIGAttendanceIndicator.get_value(self.project_ids)
        self.assertEqual(percentage_cig_attendance, 1.7643312101910829)

    def test_cddc_management_count_indicator(self):
        self._result_indicator_setup()
        cddc_management_count = \
            CDDCManagemnentCountIndicator.get_value('q_2')
        self.assertEqual(cddc_management_count, 1)

    def test_project_mapping_indicator(self):
        self._result_indicator_setup()
        project_mapping_count = ProjectMappingIndicator.get_value()
        self.assertEqual(project_mapping_count, 7)

    def test_financial_information_indicator(self):
        self._result_indicator_setup()
        project_mapping_count = \
            FinancialInformationIndicator.get_value(self.project_ids)
        self.assertEqual(project_mapping_count, 7)
