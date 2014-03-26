from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd.libs.import_project_data import(
    fetch_data,
    add_project,
    populate_reports_table

)
from wkcdd.tests.test_base import TestBase
from wkcdd import constants


class TestUtil(TestBase):
    def test_populate_projects_table(self):
        count = Project.count()
        form, project_code = constants.PROJECT_REGISTRATION_FORMS[0]
        add_project(self.project_submission[0], project_code)
        self.assertEquals(Project.count(), (count + 1))

    def test_populate_report_table_with_valid_project(self):
        self.setup_test_data()
        count = Report.count()
        form, project_code = constants.PROJECT_REPORT_FORMS[1]
        populate_reports_table([self.report_submission[0]], project_code)
        self.assertEquals(Report.count(), (count + 1))

    def test_fetch_data(self):
        form_id = constants.DAIRY_COWS_PROJECT_REGISTRATION
        raw_data = fetch_data(form_id)
        self.assertIsInstance(raw_data, list)
        self.assertTrue(len(raw_data) > 0)
        self.assertIsInstance(raw_data[0], dict)
        self.assertIn(constants.PROJECT_TYPE, raw_data[0])
        self.assertIn(constants.COUNTY, raw_data[0])
