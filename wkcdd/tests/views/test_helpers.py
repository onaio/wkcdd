import unittest
from pyramid.events import NewRequest
from pyramid import testing

from wkcdd.libs.utils import humanize
from wkcdd.tests.test_base import TestBase
from wkcdd.views.helpers import (
    requested_xlsx_format,
    build_dataset
)
from wkcdd.models import Location, County, Report, Project


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
