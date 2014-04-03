import datetime
import json
import os

from wkcdd.tests.test_base import TestBase
from wkcdd.models.report import Report
from wkcdd.models.project import Project
from wkcdd.models import County
from wkcdd import constants


class TestReport(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == "YH9T")
        json_data = json.load(open(os.path.join(
            self.test_dir, 'fixtures', 'submission_x.json')))
        self.assertEquals(report.report_data, json_data)

    def test_add_report_submission(self):
        project_code = 'TG1F'
        community = self._add_community()
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
        self.assertEquals(impact_indicators['no_of_b_increased_income'], '1')
        self.assertEquals(impact_indicators['no_of_b_improved_houses'], '1')
        self.assertEquals(impact_indicators['no_of_b_hh_assets'], '3')
        self.assertEquals(impact_indicators['no_of_children'], '3')

    def test_calculate_dairy_cow_performance_indicators(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == 'YH9T')
        performance_indicators = report.\
            calculate_performance_indicators()
        self.assertEquals(
            performance_indicators['exp_contribution'], '56000')
        self.assertEquals(
            performance_indicators['actual_contribution'], '96800')
        self.assertEquals(
            performance_indicators['community_contribution'], '173')
        self.assertEquals(
            performance_indicators['cws_proceeds_percentage'], '0')
        self.assertEquals(
            performance_indicators['db_achievement'], '10')
        self.assertEquals(
            performance_indicators['mb_achievement'], '4')
        self.assertEquals(
            performance_indicators['fb_achievement'], '6')
        self.assertEquals(
            performance_indicators['vb_achievement'], '4')
        self.assertEquals(
            performance_indicators['milk_grp_sale_percentage'], '30')

    def test_calculate_dairy_goat_performance_indicators(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == 'JDCV')
        performance_indicators = report.calculate_performance_indicators()
        self.assertEquals(
            performance_indicators['exp_contribution'], '136275')
        self.assertEquals(
            performance_indicators['actual_contribution'], '152300')
        self.assertEquals(
            performance_indicators['community_contribution'], '112')
        self.assertEquals(
            performance_indicators['bucks_target'], '1')
        self.assertEquals(
            performance_indicators['bucks_achievement'], '1')
        self.assertEquals(
            performance_indicators['bucks_percentage'], '100')
        self.assertEquals(
            performance_indicators['does_proceeds_target'], '7')
        self.assertEquals(
            performance_indicators['does_proceeds_achievement'], '8')
        self.assertEquals(
            performance_indicators['does_proceeds_percentage'], '114')
        self.assertEquals(
            performance_indicators['milk_bnf_sale_percentage'], '0')

    def test_calculate_fic_performance_indicators(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == 'KYJ7')
        performance_indicators = report.calculate_performance_indicators()
        self.assertEquals(
            performance_indicators['exp_contribution'], '6000')
        self.assertEquals(
            performance_indicators['actual_contribution'], '15400')
        self.assertEquals(
            performance_indicators['community_contribution'], '257')
        self.assertEquals(
            performance_indicators['pm_target'], '660')
        self.assertEquals(
            performance_indicators['pm_achievement'], '0')
        self.assertEquals(
            performance_indicators['pm_percentage'], '0')
        self.assertEquals(
            performance_indicators['pm_proceeds_target'], '208')
        self.assertEquals(
            performance_indicators['pm_proceeds_achievement'], '0')
        self.assertEquals(
            performance_indicators['pm_proceeds_percentage'], '0')
        self.assertEquals(
            performance_indicators['acreage_target'], '22')
        self.assertEquals(
            performance_indicators['crop_yield_target'], '452')

    def test_calculate_bodaboda_performance_indicators(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == 'YHCX')
        performance_indicators = report.calculate_performance_indicators()
        self.assertEquals(
            performance_indicators['exp_contribution'], '24000')
        self.assertEquals(
            performance_indicators['actual_contribution'], '24000')
        self.assertEquals(
            performance_indicators['community_contribution'], '100')
        self.assertEquals(
            performance_indicators['db_target'], '180')
        self.assertEquals(
            performance_indicators['mb_target'], '80')
        self.assertEquals(
            performance_indicators['fb_target'], '100')
        self.assertEquals(
            performance_indicators['mbs_proceeds_target'], '4')
        self.assertEquals(
            performance_indicators['grp_target'], '108000')
        self.assertEquals(
            performance_indicators['bnf_income_target'], '180000')

    def test_calculate_poultry_performance_indicators(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == 'DRT4')
        performance_indicators = report.calculate_performance_indicators()
        self.assertEquals(
            performance_indicators['exp_contribution'], '146600')
        self.assertEquals(
            performance_indicators['actual_contribution'], '162250')
        self.assertEquals(
            performance_indicators['community_contribution'], '111')
        self.assertEquals(
            performance_indicators['db_target'], '43')
        self.assertEquals(
            performance_indicators['mb_target'], '22')
        self.assertEquals(
            performance_indicators['fb_target'], '21')
        self.assertEquals(
            performance_indicators['pu_target'], '20')
        self.assertEquals(
            performance_indicators['db_target'], '43')
        self.assertEquals(
            performance_indicators['mb_target'], '22')
        self.assertEquals(
            performance_indicators['fb_target'], '21')
        self.assertEquals(
            performance_indicators['vb_target'], '9')
        self.assertEquals(
            performance_indicators['cr_target'], '4000')
        self.assertEquals(
            performance_indicators['bsold_target'], '3600')
        self.assertEquals(
            performance_indicators['eprd_target'], '1200')
        self.assertEquals(
            performance_indicators['grp_target'], '100000')
        self.assertEquals(
            performance_indicators['bnf_income_target'], '5000')

    # 1. Passing an empty project list should return None
    # 2. Passing a project list with one project should return data based
    # on that project
    # 3. Passing a list of projects should calculate impact and performance
    # aggregator totals
    def test_impact_indicator_aggregation_with_no_projects(self):
        results = Report.get_aggregated_impact_indicators(None)
        self.assertEqual(results['indicator_list'], None)
        self.assertEqual(results['summary'], None)

    def test_impact_indicator_aggregation_with_no_reports(self):
        self.setup_test_data()
        project = Project.get(Project.code == 'NOREPORT')
        results = Report.get_aggregated_impact_indicators([project])
        project_indicators_map = results['indicator_list'][0]
        self.assertFalse(project_indicators_map['indicators'])
        self.assertEqual(project_indicators_map['project_id'], project.id)
        self.assertFalse(results['summary'])

    def test_impact_indicator_aggregation_with_one_project(self):
        self.setup_test_data()
        project_code = 'YH9T'
        project = Project.get(Project.code == project_code)
        results = Report.get_aggregated_impact_indicators([project])
        summary = results['summary']
        project_indicators_map = results['indicator_list'][0]
        self.assertEqual(project_indicators_map['project_id'], project.id)
        self.assertEqual(
            project_indicators_map['indicators']['no_of_b_hh_assets'], '3')
        self.assertEqual(summary['no_of_b_improved_houses'], 1)
        self.assertEqual(summary['no_of_b_increased_income'], 1)

    def test_impact_indicator_aggregation_with_many_projects(self):
        self.setup_test_data()
        project_code_list = ['YH9T', 'JDCV']
        project_list = []
        for code in project_code_list:
            project = Project.get(Project.code == code)
            project_list.append(project)
        results = Report.get_aggregated_impact_indicators(project_list)
        summary = results['summary']
        project_indicators_a = results['indicator_list'][0]
        project_indicators_b = results['indicator_list'][1]
        self.assertEqual(
            project_indicators_a['project_id'], project_list[0].id)
        self.assertEqual(
            project_indicators_b['project_id'], project_list[1].id)
        self.assertTrue(
            'no_of_b_hh_assets' in project_indicators_a['indicators'])
        self.assertEqual(summary['no_of_b_improved_houses'], 1)
        self.assertEqual(summary['no_of_b_increased_income'], 16)
        self.assertEqual(summary['no_of_children'], 8)
        self.assertEqual(summary['no_of_b_hh_assets'], 3)

    def test_performance_indicator_aggregation_with_one_project(self):
        self.setup_test_data()
        project_code = 'YH9T'
        project = Project.get(Project.code == project_code)
        results = Report.get_aggregated_performance_indicators(
            [project],
            constants.DAIRY_COWS_PROJECT_REPORT)
        project_indicators_map = results['indicator_list'][0]
        summary = results['summary']
        self.assertEqual(
            project_indicators_map['indicators']['exp_contribution'], '56000')
        self.assertEqual(
            project_indicators_map['indicators']['community_contribution'],
            '173')
        self.assertEqual(
            project_indicators_map['indicators']['vb_achievement'], '4')
        self.assertNotIn('no_of_children',
                         project_indicators_map['indicators'])
        self.assertEqual(summary['community_contribution'], 173)
        self.assertEqual(summary['vb_percentage'], 80)

    def test_performance_indicator_aggregation_with_many_projects(self):
        self.setup_test_data()
        project_code_list = ['YH9T', '7CWA']
        project_list = []
        for code in project_code_list:
            project = Project.get(Project.code == code)
            project_list.append(project)
        results = Report.get_aggregated_performance_indicators(
            project_list,
            constants.DAIRY_COWS_PROJECT_REPORT)
        project_indicators_a = results['indicator_list'][0]
        project_indicators_b = results['indicator_list'][1]
        summary = results['summary']
        self.assertEqual(
            project_indicators_a['project_id'], project_list[0].id)
        self.assertEqual(
            project_indicators_b['project_id'], project_list[1].id)
        self.assertTrue(
            'exp_contribution' in project_indicators_a['indicators']
            and 'exp_contribution' in project_indicators_b['indicators'])
        self.assertTrue(
            'community_contribution' in project_indicators_a['indicators']
            and 'community_contribution' in project_indicators_b['indicators'])
        self.assertEqual(summary['community_contribution'], 136.5)
        self.assertEqual(summary['vb_percentage'], 46)

    def test_get_location_indicator_aggregation(self):
        self.setup_test_data()
        counties = County.all()
        results = Report.get_location_indicator_aggregation(counties)
        self.assertIsNotNone(results['aggregated_impact_indicators']
                             [counties[0].id])
        self.assertEquals(len(results['total_indicator_summary']), 4)

    def test_performance_indicator_calculation_on_legacy_data(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == '7CWA')
        performance_indicators = report.\
            calculate_performance_indicators()
        self.assertEquals(
            performance_indicators['exp_contribution'], '624800')
        self.assertEquals(
            performance_indicators['actual_contribution'], '624800')
        self.assertEquals(
            performance_indicators['community_contribution'], '100')
        self.assertEquals(
            performance_indicators['cws_proceeds_percentage'], '22')
        self.assertEquals(
            performance_indicators['db_achievement'], '13')
        self.assertEquals(
            performance_indicators['mb_achievement'], '7')
        self.assertEquals(
            performance_indicators['fb_achievement'], '6')
        self.assertEquals(
            performance_indicators['vb_achievement'], '3')
        self.assertEquals(
            performance_indicators['milk_grp_sale_percentage'], '32')
