import os
import json
from pyramid.events import NewRequest
from pyramid import testing

from wkcdd.tests.test_base import (
    TestBase,
    _load_json_fixture
)
from wkcdd.libs.utils import (
    number_to_month_name,
    get_impact_indicator_list)
from wkcdd.views.helpers import (
    SUB_COUNTIES_LEVEL,
    MONTH_PERIOD,
    QUARTER_PERIOD,
    requested_xlsx_format,
    get_project_geolocations,
    get_geolocations_from_items,
    get_target_class_from_view_by,
    get_sector_data,
    get_performance_sector_mapping,
    build_report_period_criteria,
    generate_time_series,
    process_trend_parameters,
    get_impact_indicator_trend_report)
from wkcdd import constants
from wkcdd.models import (
    County,
    Project,
    SubCounty,
    Community,
    Report

)


class TestHelpers(TestBase):

    def test_requested_xlsx_format(self):
        request = testing.DummyRequest()
        request.GET['format'] = 'xlsx'
        event = NewRequest(request)
        requested_xlsx_format(event)
        self.assertEqual(request.override_renderer, 'xlsx')

    def test_dont_override_renderer_if_not_requested(self):
        request = testing.DummyRequest()
        event = NewRequest(request)
        requested_xlsx_format(event)
        self.assertFalse(hasattr(request, 'override_renderer'))

    def test_get_target_class_from_view_by_returns_child_class_if_none(self):
        target_class = get_target_class_from_view_by(None, County)
        self.assertEqual(target_class, SubCounty)

    def test_get_target_class_from_view_by_raises_value_error_if_both_none(
            self):
        self.assertRaises(
            ValueError, get_target_class_from_view_by, None)

    def test_get_target_class_from_view_by_returns_class_from_name(self):
        target_class = get_target_class_from_view_by(SUB_COUNTIES_LEVEL, None)
        self.assertEqual(target_class, SubCounty)

    def test_get_project_geolocations(self):
        self.setup_test_data()
        geopoints = json.dumps(_load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', 'geopoints.json')))
        projects = Project.all()
        project_geopoints = get_project_geolocations(projects)

        self.assertEquals(json.dumps(project_geopoints), geopoints)

    def test_get_sector_data_for_community_cow_projects(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Maragoli")
        sector_id = constants.DAIRY_COWS_PROJECT_REGISTRATION
        reg_id, report_id, label = get_performance_sector_mapping(sector_id)[0]
        results = get_sector_data(sector_id, report_id, [community])

        self.assertEqual(len(results['rows']), 1)

    def test_get_sector_data_for_cow_project(self):
        self.setup_test_data()
        project = Project.get(Project.code == "7CWA")
        sector_id = constants.DAIRY_COWS_PROJECT_REGISTRATION
        reg_id, report_id, label = get_performance_sector_mapping(sector_id)[0]
        results = get_sector_data(sector_id, report_id, [project])

        self.assertEqual(len(results['rows']), 1)
        summary_row = results['summary_row']
        self.assertEqual(summary_row['exp_contribution'], 624800)

    def test_build_report_period_criteria(self):
        self.setup_report_period_test_data()
        period = '2013_14'
        month = '8'
        project = Project.get(Project.code == "7CWA")

        # Test when month is Aug(8) 2013_14
        report = Report.get(
            Report.period == period,
            Report.month == month)

        criteria = build_report_period_criteria(month, period)

        reports = Report.get_reports_for_projects([project], *criteria)
        self.assertEqual(len(reports), 1)
        self.assertIn(report, reports)

    def test_get_geolocations_from_items(self):
        self.setup_test_data()
        geopoints = json.dumps(_load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', 'cow_project_1_geopoints.json')))
        sector_id = constants.DAIRY_COWS_PROJECT_REGISTRATION
        projects = Project.all()
        project_geopoints = get_geolocations_from_items(projects, sector_id)

        self.assertEquals(json.dumps(project_geopoints), geopoints)

    def test_generate_time_series_with_months(self):
        self.setup_report_trends_data()
        time_series = generate_time_series(1, 12, MONTH_PERIOD, '2012_13')
        self.assertEqual(time_series, [1, 5])

    def test_generate_time_series_with_quarters(self):
        self.setup_report_trends_data()
        time_series = generate_time_series(
            'q_1', 'q_4', QUARTER_PERIOD, '2012_13')
        self.assertEqual(time_series, ['q_1', 'q_2'])

    def test_impact_indicator_report_trends_for_month_data(self):
        self.setup_report_trends_data()
        locations = County.all()
        time_series = [1, 5, 8]

        indicators = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)

        time_series, series_data_map, series_labels = (
            get_impact_indicator_trend_report(
                time_series, MONTH_PERIOD, '2012_13', indicators, locations))

        self.assertEqual(time_series, [1, 5, 8])
        self.assertEqual(series_labels, [c.name for c in locations])

        self.assertEqual(
            series_data_map['impact_information/b_income'],
            [[
                [number_to_month_name(1), 1],
                [number_to_month_name(5), 1],
                [number_to_month_name(8), 0]],
             [
                 [number_to_month_name(1), 0],
                 [number_to_month_name(5), 0],
                 [number_to_month_name(8), 0]]
             ])
        self.assertEqual(
            series_data_map['impact_information/no_children'],
            [[
                [number_to_month_name(1), 3],
                [number_to_month_name(5), 3],
                [number_to_month_name(8), 0]],
             [
                 [number_to_month_name(1), 0],
                 [number_to_month_name(5), 0],
                 [number_to_month_name(8), 0]]
             ])

    def test_process_trend_parameters(self):
        self.setup_report_trends_data()
        counties = County.all()
        periods = Report.get_periods_for(counties)
        param_start = '1'
        param_end = '6'
        param_year = '2012_13'

        start_period, end_period, year = (
            process_trend_parameters(
                periods, param_start, param_end, param_year))

        self.assertEqual(start_period, '1')
        self.assertEqual(end_period, '12')
        self.assertEqual(year, param_year)
