from pyramid import testing

from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)
from wkcdd.views.projects import ProjectViews


class TestProjectViews(IntegrationTestBase):
    def setUp(self):
        super(TestProjectViews, self).setUp()
        self.request = testing.DummyRequest()
        self.project_views = ProjectViews(self.request)

    def test_project_list_return_all_projects(self):
        self.setup_test_data()
        response = self.project_views.list_all_projects()
        self.assertEquals(len(response['projects']), 3)

    def test_project_details_returns_report_list(self):
        pass

    def test_project_report_trend_over_time(self):
        pass


class TestProjectViewsFunctional(FunctionalTestBase):

    def test_project_list_return_all_projects_views(self):
        pass
