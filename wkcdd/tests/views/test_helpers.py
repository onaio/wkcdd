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
    get_project_geolocations,
    name_to_location_type,
    get_target_class_from_view_by,
    PROJECT_LEVEL, COUNTIES_LEVEL, SUB_COUNTIES_LEVEL, CONSTITUENCIES_LEVEL,
    COMMUNITIES_LEVEL, PROJECTS_LEVEL)
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

    def test_name_to_location_type(self):
        self.assertEqual(name_to_location_type(PROJECT_LEVEL), Project)
        self.assertEqual(name_to_location_type(COUNTIES_LEVEL), County)
        self.assertEqual(name_to_location_type(SUB_COUNTIES_LEVEL), SubCounty)
        self.assertEqual(
            name_to_location_type(CONSTITUENCIES_LEVEL), Constituency)
        self.assertEqual(
            name_to_location_type(COMMUNITIES_LEVEL), Community)

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
        self.assertEquals(dataset['headers'][1],
                          humanize(Location.SUB_COUNTY).title())
        self.assertEquals(dataset['rows'][0][1].name,
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
        self.assertEquals(dataset['headers'][3],
                          humanize(Location.COMMUNITY).title())
        self.assertEquals(dataset['rows'][0][4].name,
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
        self.assertEquals(teso_sub_county_row[1].name, sub_county.name)

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

        results = generate_performance_indicators_for(location_map, "projects")
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
        self.assertIsNotNone(results['project_types'])
        indicator_labels = results['sector_indicator_mapping']
        self.assertNotIn('Dairy Cows', indicator_labels)

    def test_all_county_view_by_constituencies(self):
        self.setup_test_data()
        constituency = Constituency.get(Constituency.name == 'Kakamega')
        location_map = self.setup_location_map()

        results = generate_performance_indicators_for(
            location_map,
            level='constituencies')

        rows = (results['sector_aggregated_indicators']
                [constants.DAIRY_COWS_PROJECT_REGISTRATION]
                ['rows'])
        self.assertIsNotNone(results['project_types'])
        constituencies_in_dataset = [row[2] for row in rows]
        self.assertEquals(constituencies_in_dataset, [constituency])

    def test_all_county_view_by_communities(self):
        self.setup_test_data()
        communities = Community.all(Community.name.in_(["Maragoli", "Bukusu"]))
        location_map = self.setup_location_map()

        results = generate_performance_indicators_for(
            location_map,
            level='communities')

        rows = (results['sector_aggregated_indicators']
                [constants.DAIRY_COWS_PROJECT_REGISTRATION]
                ['rows'])
        self.assertIsNotNone(results['project_types'])
        communities_in_dataset = [row[3] for row in rows]
        self.assertEquals(communities_in_dataset, communities)

    def test_only_relevant_communities_display_for_sub_county(self):
        self.setup_test_data()
        # Test for location filtering on dairy cow projects
        counties = County.all(County.name == "Bungoma")

        results = generate_performance_indicators_for(None, level='counties')

        rows = (results['sector_aggregated_indicators']
                [constants.DAIRY_COWS_PROJECT_REGISTRATION]
                ['rows'])
        counties_in_dataset = [row[0] for row in rows]
        self.assertEqual(counties_in_dataset, counties)

        # Test location filtering on dairy goat projects
        counties = County.all(County.name != "Siaya")
        rows = (results['sector_aggregated_indicators']
                [constants.DAIRY_GOAT_PROJECT_REGISTRATION]
                ['rows'])
        counties_in_dataset = [row[0] for row in rows]
        self.assertEqual(counties_in_dataset, counties)

    def test_all_county_view_by_project(self):
        self.setup_test_data()
        projects = Project.all(Project.code.in_(["7CWA", "YH9T"]))
        location_map = self.setup_location_map()

        results = generate_performance_indicators_for(
            location_map,
            level='projects')

        rows = (results['sector_aggregated_indicators']
                [constants.DAIRY_COWS_PROJECT_REGISTRATION]
                ['rows'])
        self.assertIsNotNone(results['project_types'])
        projects_in_dataset = [row[4] for row in rows]
        self.assertEquals(projects_in_dataset, projects)
