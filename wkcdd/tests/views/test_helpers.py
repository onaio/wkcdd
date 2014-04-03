import unittest
from pyramid.events import NewRequest
from pyramid import testing

from wkcdd.views.helpers import requested_xlsx_format


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

