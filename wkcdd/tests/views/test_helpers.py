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
    filter_projects_by,
    get_project_geolocations
)
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
        self.assertEquals(dataset['headers'][0],
                          humanize(Location.COMMUNITY).title())
        self.assertEquals(dataset['rows'][0][0].name,
                          "Dairy Goat Project Center 1")
        self.assertEquals(dataset['summary_row'], [20, 1, 3, 8])


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

        search_criteria = {"location": {"community": '',
                                        "constituency": '',
                                        "sub_county": '',
                                        "county": county1.id
                                        }
                           }
        projects = filter_projects_by(search_criteria)
        self.assertEqual(len(projects), 0)

        search_criteria = {"location": {"community": '',
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
        search_criteria = {"location": {"community": '',
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
        search_criteria = {"location": {"community": '',
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
        search_criteria = {"location": {"community": community.id,
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
            "location": {"community": community.id,
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
