from pyramid import testing

from wkcdd.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)
from wkcdd.views.default_views import private


class TestProjectViews(IntegrationTestBase):
    def test_project_list_return_all_projects(self):
        pass

    def test_project_details_returns_report_list(self):
        pass

    def test_project_report_trend_over_time(self):
        pass
