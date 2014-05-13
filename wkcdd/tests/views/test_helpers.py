import os
import json
from pyramid.events import NewRequest
from pyramid import testing

from wkcdd.tests.test_base import (
    TestBase,
    _load_json_fixture
)
from wkcdd.views.helpers import (
    SUB_COUNTIES_LEVEL,
    requested_xlsx_format,
    get_project_geolocations,
    get_target_class_from_view_by,
    get_sector_data,
    get_performance_sector_mapping)
from wkcdd import constants
from wkcdd.models import (
    County,
    Project,
    SubCounty,
    Community
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
        self.assertEquals(project_geopoints, geopoints)

    def test_get_sector_data_for_community_cow_projects(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Maragoli")
        sector = constants.DAIRY_COWS_PROJECT_REGISTRATION
        reg_id, report_id, label = get_performance_sector_mapping(sector)[0]
        results = get_sector_data(sector, report_id, [community])

        self.assertEqual(len(results['rows']), 1)

    def test_get_sector_data_for_cow_project(self):
        self.setup_test_data()
        project = Project.get(Project.code == "7CWA")
        sector = constants.DAIRY_COWS_PROJECT_REGISTRATION
        reg_id, report_id, label = get_performance_sector_mapping(sector)[0]
        results = get_sector_data(sector, report_id, [project])

        self.assertEqual(len(results['rows']), 1)
        summary_row = results['summary_row']
        self.assertEqual(summary_row['exp_contribution'], 624800)
