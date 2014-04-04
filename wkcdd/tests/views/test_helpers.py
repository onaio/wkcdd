import unittest
from pyramid.events import NewRequest
from pyramid import testing
from wkcdd.tests.test_base import TestBase

from wkcdd.views.helpers import (
    requested_xlsx_format,
    build_dataset
)
from wkcdd.models import Location, County, Report
from wkcdd import constants


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
    def test_build_impact_indicator_dataset(self):
        self.setup_test_data()
        counties = County.all()
        impact_indicators = \
            Report.get_location_indicator_aggregation(counties)
        dataset = build_dataset(Location.COUNTY,
                                counties,
                                constants,
                                impact_indicators)
        self.assertEquals(dataset['headers'][0], Location.COUNTY)
        self.assertEquals(dataset['rows'][0][0].name, "Bungoma")
        self.assertEquals(dataset['summary_row'], [20, 1, 3, 8])
