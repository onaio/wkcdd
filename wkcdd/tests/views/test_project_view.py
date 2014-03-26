from pyramid import testing

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
        self.assertEqual(len(response['projects']), 3)
        self.assertEqual(len(response['project_types']), 2)
        self.assertEquals(response['locations'][1][0].name, 'Bungoma')

    def test_project_details_returns_report_list(self):
        self.setup_test_data()
        project = Project.get(Project.code == 'YH9T')
        self.request.context = project
        response = self.project_views.show()
        self.assertIsInstance(response['project'], Project)
        self.assertEqual(response['project'].id, project.id)

    def test_project_report_trend_over_time(self):
        pass


class TestProjectViewsFunctional(FunctionalTestBase):

    def test_project_list_return_all_projects_views(self):
        pass
