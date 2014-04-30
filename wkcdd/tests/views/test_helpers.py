import unittest
import os
import json
from pyramid.events import NewRequest
from pyramid import testing

from wkcdd.libs.utils import humanize
from wkcdd.tests.test_base import (
    TestBase,
    IntegrationTestBase,
    _load_json_fixture
)
from wkcdd.views.helpers import (
    requested_xlsx_format,
    build_dataset,
    build_performance_dataset,
    filter_projects_by,
    generate_impact_indicators_for,
    generate_performance_indicators_for,
    get_project_geolocations)
from wkcdd import constants
from wkcdd.models import (
    Location,
    County,
    Report,
    Project,
    SubCounty,
    Community,
    Constituency
)


class TestHelpers(unittest.TestCase):
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


class TestBuildDatasetHelpers(TestBase):
    def test_build_dataset(self):
        self.setup_test_data()
        counties = County.all()
        impact_indicators = \
            Report.get_impact_indicator_aggregation_for(counties)
        dataset = build_dataset(Location.COUNTY,
                                counties,
                                impact_indicators)
        self.assertEquals(dataset['headers'][0],
                          humanize(Location.COUNTY).title())
        self.assertEquals(dataset['rows'][0][0].name, "Bungoma")
        self.assertEquals(dataset['summary_row'], [20, 1, 3, 8])

    def test_build_dataset_with_projects_list(self):
        self.setup_test_data()
        projects = Project.all()
        impact_indicators = (
            Report.get_aggregated_impact_indicators(projects))
        dataset = build_dataset(Location.COMMUNITY,
                                None,
                                impact_indicators,
                                projects
                                )
        self.assertEquals(dataset['headers'][3],
                          humanize(Location.COMMUNITY).title())
        self.assertEquals(dataset['rows'][0][4].name,
                          "Dairy Goat Project Center 1")
        self.assertEquals(dataset['summary_row'], [20, 1, 3, 8])

    def test_build_dataset_for_performance_indicators(self):
        self.setup_test_data()
        county = County.get(County.name == "Busia")
        sub_counties = county.children()
        performance_indicators = (
            Report.get_performance_indicator_aggregation_for(
                county.children(), constants.DAIRY_GOAT_PROJECT_REPORT))
        sector_report_map = (
            constants.PERFORMANCE_INDICATOR_REPORTS
            [constants.DAIRY_GOAT_PROJECT_REPORT])
        dataset = build_performance_dataset(
            Location.SUB_COUNTY,
            sub_counties,
            performance_indicators,
            sector_report_map=sector_report_map)
        self.assertEquals(dataset['headers'][0],
                          humanize(Location.SUB_COUNTY).title())
        self.assertEquals(dataset['rows'][0][0].name,
                          sub_counties[0].name)

    def test_build_dataset_for_performance_project_list(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Rwatama")
        projects = community.projects
        performance_indicators = (
            Report.get_performance_indicator_aggregation_for(
                [community], constants.DAIRY_GOAT_PROJECT_REPORT))

        sector_report_map = (
            constants.PERFORMANCE_INDICATOR_REPORTS
            [constants.DAIRY_GOAT_PROJECT_REPORT])

        dataset = build_performance_dataset(
            Location.COMMUNITY,
            [community],
            performance_indicators,
            projects=projects,
            sector_report_map=sector_report_map)
        self.assertEquals(dataset['headers'][0],
                          humanize(Location.COMMUNITY).title())
        self.assertEquals(dataset['rows'][0][0].name,
                          projects[0].name)
        self.assertEquals(dataset['summary_row'][0], [24000, 24000, 100.0])


class TestProjectFilter(IntegrationTestBase):
    def test_filter_projects_by_name(self):
        self.setup_community_test_data()
        search_value = "Cow project 1"
        search_criteria = {"name": search_value}
        projects = filter_projects_by(search_criteria)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, search_value)

    def test_filter_projects_by_sector(self):
        self.setup_test_data()
        search_criteria = {"sector": constants.DAIRY_COWS_PROJECT_REGISTRATION}
        projects = filter_projects_by(search_criteria)
        self.assertEqual({project.sector for project in projects},
                         {constants.DAIRY_COWS_PROJECT_REGISTRATION})

    def test_filter_projects_by_county(self):
        self.setup_test_data()
        county1 = County.get(County.name == "Siaya")
        county2 = County.get(County.name == "Bungoma")

        search_criteria = {"location_map": {"community": '',
                                            "constituency": '',
                                            "sub_county": '',
                                            "county": county1.id
                                            }
                           }
        projects = filter_projects_by(search_criteria)
        self.assertEqual(len(projects), 0)

        search_criteria = {"location_map": {"community": '',
                                            "constituency": '',
                                            "sub_county": '',
                                            "county": county2.id
                                            }
                           }
        projects = filter_projects_by(search_criteria)
        self.assertEqual(len(projects), 6)

    def test_filter_projects_by_sub_county(self):
        self.setup_test_data()
        sub_county1 = SubCounty.get(SubCounty.name == "Teso")
        search_criteria = {"location_map": {"community": '',
                                            "constituency": '',
                                            "sub_county": sub_county1.id,
                                            "county": ''
                                            }
                           }

        projects = filter_projects_by(search_criteria)
        self.assertEqual(len(projects), 1)

    def test_filter_projects_by_constituency(self):
        self.setup_community_test_data()
        constituency = Constituency.get(Constituency.name == "sirisia")
        search_criteria = {"location_map": {"community": '',
                                            "constituency": constituency.id,
                                            "sub_county": '',
                                            "county": ''
                                            }
                           }

        projects = filter_projects_by(search_criteria)
        self.assertEqual(len(projects), 4)

    def test_filter_projects_by_community(self):
        self.setup_community_test_data()
        community = Community.get(Community.name == "lutacho")
        search_criteria = {"location_map": {"community": community.id,
                                            "constituency": '',
                                            "sub_county": '',
                                            "county": ''
                                            }
                           }

        projects = filter_projects_by(search_criteria)
        self.assertEqual(len(projects), 4)

    def test_filter_with_multiple_criteria(self):
        self.setup_test_data()
        project = Project.get(Project.code == "JDCV")
        search_criteria = {
            "sector": constants.DAIRY_GOAT_PROJECT_REGISTRATION,
            "name": "Project Center 2"
        }
        projects = filter_projects_by(search_criteria)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0], project)

    def test_filter_with_location(self):
        self.setup_test_data()
        project = Project.get(Project.code == "YH9T")
        community = Community.get(Community.name == "Bukusu")
        search_criteria = {
            "name": "Project Center 1",
            "location_map": {"community": community.id,
                             "constituency": '',
                             "sub_county": '',
                             "county": ''
                             }
        }
        projects = filter_projects_by(search_criteria)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0], project)

    def test_get_project_geolocations(self):
        self.setup_test_data()
        geopoints = json.dumps(_load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', 'geopoints.json')))
        projects = Project.all()
        project_geopoints = get_project_geolocations(projects)
        self.assertEquals(project_geopoints, geopoints)


class TestImpactIndicatorGeneration(TestBase):
    def test_generate_impact_indicators_for_none(self):
        self.setup_test_data()
        results = generate_impact_indicators_for(None)

        self.assertEqual(results['aggregate_list'], County.all())
        self.assertEqual(results['aggregate_type'], Location.COUNTY)

        impact_indicators = results['impact_indicators']
        self.assertIn('aggregated_impact_indicators', impact_indicators)
        self.assertIn('total_indicator_summary', impact_indicators)

    def test_generate_impact_indicators_for_county(self):
        self.setup_test_data()
        county = County.get(County.name == "Busia")

        location_map = {
            "community": '',
            "constituency": '',
            "sub_county": '',
            "county": "{}".format(county.id)
        }

        results = generate_impact_indicators_for(location_map)

        self.assertEqual(results['aggregate_list'], county.children())
        self.assertEqual(results['aggregate_type'], Location.SUB_COUNTY)

        impact_indicators = results['impact_indicators']
        self.assertIn('aggregated_impact_indicators', impact_indicators)
        self.assertIn('total_indicator_summary', impact_indicators)

    def test_generate_impact_indicators_for_community(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Rwatama")
        location_map = {
            "community": community.id,
            "constituency": '',
            "sub_county": '',
            "county": ""
        }

        results = generate_impact_indicators_for(location_map, "projects")

        self.assertEqual(results['aggregate_type'], 'Project')
        self.assertEqual(results['aggregate_list'], community.projects)

    def test_generate_impact_indicators_for_county_view_by_levels(self):
        self.setup_test_data()
        county = County.get(County.name == "Bungoma")
        location_map = {
            "community": '',
            "constituency": '',
            "sub_county": '',
            "county": "{}".format(county.id)
        }

        view_by = "sub_counties"
        results = generate_impact_indicators_for(location_map, view_by)

        self.assertEqual(results['aggregate_list'], county.children())
        self.assertEqual(results['aggregate_type'], Location.SUB_COUNTY)

        view_by = "constituencies"
        results = generate_impact_indicators_for(location_map, view_by)
        constituencies = [constituencies
                          for sub_counties in county.children()
                          for constituencies in sub_counties.children()]
        self.assertEqual(results['aggregate_list'], constituencies)
        self.assertEqual(results['aggregate_type'], Location.CONSTITUENCY)

        view_by = "communities"
        results = generate_impact_indicators_for(location_map, view_by)
        communities = [communities
                       for sub_counties in county.children()
                       for consts in sub_counties.children()
                       for communities in consts.children()]
        self.assertEqual(results['aggregate_list'], communities)
        self.assertEqual(results['aggregate_type'], Location.COMMUNITY)

        view_by = "projects"
        results = generate_impact_indicators_for(location_map, view_by)
        projects = Report.get_projects_from_location(county)
        self.assertEqual(results['aggregate_list'], projects)
        self.assertEqual(results['aggregate_type'], 'Project')


class TestPerformanceIndicatorGeneration(TestBase):
    def setup_location_map(self,
                           community='',
                           constituency='',
                           sub_county='',
                           county=''):
        return {
            "community": community,
            "constituency": constituency,
            "sub_county": sub_county,
            "county": county
        }

    def test_generate_performance_indicators_for_none(self):
        self.setup_test_data()
        results = generate_performance_indicators_for(None, level='counties')
        self.assertIsNotNone(results['project_types'])
        self.assertEqual(results['aggregate_list'], County.all())

    def test_generate_performance_indicators_for_county(self):
        self.setup_test_data()
        county = County.get(County.name == "Busia")
        sub_county = SubCounty.get(SubCounty.name == "Teso")
        location_map = self.setup_location_map(
            county="{}".format(county.id))

        results = generate_performance_indicators_for(
            location_map)
        self.assertIsNotNone(results['project_types'])

        teso_sub_county_row = (
            results['sector_aggregated_indicators']
            [constants.DAIRY_GOAT_PROJECT_REGISTRATION]
            ['rows'][0])
        self.assertEquals(teso_sub_county_row[0].name, sub_county.name)

    def test_generate_performance_indicators_for_constituency(self):
        self.setup_test_data()
        constituency = Constituency.get(Constituency.name == "Amagoro")
        location_map = self.setup_location_map(
            constituency="{}".format(constituency.id))

        results = generate_performance_indicators_for(
            location_map)
        self.assertEqual(results['aggregate_list'],
                         constituency.children())

    def test_generate_performance_indicators_for_community(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Rwatama")
        location_map = self.setup_location_map(
            community="{}".format(community.id))

        results = generate_performance_indicators_for(location_map)
        self.assertIsNotNone(results['project_types'])

    def test_generate_performance_indicators_for_community_sector(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Rwatama")
        location_map = self.setup_location_map(
            community="{}".format(community.id))

        results = generate_performance_indicators_for(
            location_map,
            constants.DAIRY_COWS_PROJECT_REGISTRATION
        )
        self.assertFalse(results['sector_aggregated_indicators'])
        self.assertFalse(results['sector_indicator_mapping'])

    def test_all_county_view_by_constituencies(self):
        self.setup_community_test_data()
        constituency = Constituency.get(Constituency.name == "sirisia")
        location_map = self.setup_location_map()

        results = generate_performance_indicators_for(
            location_map,
            level='constituencies')
        self.assertIsNotNone(results['project_types'])
        sirisia_constituency_row = (
            results['sector_aggregated_indicators']
            [constants.DAIRY_COWS_PROJECT_REGISTRATION]
            ['rows'][0])
        self.assertEquals(sirisia_constituency_row[0].name, constituency.name)

    def test_all_county_view_by_communities(self):
        self.setup_community_test_data()
        community = Community.get(Community.name == "lutacho")
        location_map = self.setup_location_map()

        results = generate_performance_indicators_for(
            location_map,
            level='communities')
        self.assertIsNotNone(results['project_types'])
        sirisia_community_row = (
            results['sector_aggregated_indicators']
            [constants.DAIRY_COWS_PROJECT_REGISTRATION]
            ['rows'][0])
        self.assertEquals(sirisia_community_row[0].name, community.name)
