from pyramid import testing
from webob.multidict import MultiDict
from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)

from wkcdd.models.project import (
    Project
)

from wkcdd.views.projects import ProjectViews


class TestProjectViews(IntegrationTestBase):

    def setUp(self):
        super(TestProjectViews, self).setUp()
        self.request = testing.DummyRequest()
        self.project_views = ProjectViews(self.request)

    def test_project_list_return_all_projects(self):
        self.setup_test_data()
        response = self.project_views.list()
        count = Project.count()
        self.assertEqual(len(response['projects']), count)
        self.assertEqual(len(response['project_types']), 2)
        self.assertEquals(response['locations'][1][0].name, 'Bungoma')

    def test_show_projects_without_reports_returns_none_project(self):
        self.setup_test_data()
        project = Project.get(Project.code == 'NOREPORT')
        self.request.context = project
        response = self.project_views.show()
        self.assertEqual(response['performance_indicators'], None)
        self.assertEqual(response['impact_indicators'], None)

    def test_show_project_with_reports_returns_indicators(self):
        self.setup_test_data()
        project = Project.get(Project.code == 'YH9T')
        self.request.context = project
        response = self.project_views.show()
        self.assertIsInstance(response['project'], Project)
        self.assertEqual(response['performance_indicators'],
                         project.reports[0].get_performance_indicators())
        self.assertEqual(response['impact_indicators'],
                         project.reports[0].get_impact_indicators())

    def test_search_project_list(self):
        self.setup_test_data()
        params = MultiDict({'filter': '1',
                            'search_term': 'Dairy Goat Project Center 1'})
        self.request.GET = params
        response = self.project_views.list()
        self.assertEquals(len(response['projects']), 1)
        self.assertEquals(response['projects'][0].name,
                          'Dairy Goat Project Center 1')

    def test_filter_project_list(self):
        self.setup_test_data()

    def test_show_project_with_period_and_quarter(self):
        """
        Test filter with quarter specified
        """
        self.setup_report_period_test_data()
        project = Project.get(Project.code == '7CWA')
        self.request.context = project

        params = MultiDict({'period': '2013_14',
                            'month_or_quarter': 'q_3'})
        self.request.GET = params

        response = self.project_views.show()
        self.assertIsNotNone(response['performance_indicators'])

    def test_show_project_with_period_and_month(self):
        """
        Test filter with month specified
        """
        self.setup_report_period_test_data()
        project = Project.get(Project.code == '7CWA')
        self.request.context = project

        params = MultiDict({'period': '2012_13',
                            'month_or_quarter': '1'})
        self.request.GET = params

        response = self.project_views.show()
        self.assertIsNotNone(response['performance_indicators'])


class TestProjectViewsFunctional(FunctionalTestBase):

    def test_project_list_return_all_projects_views(self):
        self.setup_test_data()
        url = self.request.route_path('projects', traverse=())
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
