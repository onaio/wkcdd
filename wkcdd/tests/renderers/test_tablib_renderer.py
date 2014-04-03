import unittest

from pyramid import testing
from wkcdd.renderers import TablibXLSXRenderer


class TestTablibRenderer(unittest.TestCase):
    def test_renderer_output(self):
        request = testing.DummyRequest()
        renderer = TablibXLSXRenderer({})
        data = {
            'headers': ['County', "#1", "#2", '#3', '#4'],
            'rows': [
                ['Bungoma', '200', '300', '350', '100'],
                ['Lugari', '120', '210', '120', '350']],
            'summary_row': ['320', '510', '470', '450']
        }
        result = renderer(data, {'request': request})
        self.assertEqual(request.response.content_type,
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

