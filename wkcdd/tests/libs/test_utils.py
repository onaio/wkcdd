from wkcdd.models.project import Project
from wkcdd.libs import utils
from wkcdd.tests.test_base import TestBase
from wkcdd import constants
import json


class TestUtil(TestBase):
    def test_populate_projects_table(self):
        count = Project.count()
        utils.add_project(json.loads(self.submissions[0]))
        self.assertEquals(Project.count(), (count + 1))

    def test_fetch_data(self):
        form_id = constants.DAIRY_COWS_PROJECT_REGISTRATION
        raw_data = utils.fetch_data(form_id)
        self.assertIsInstance(raw_data, list)
        self.assertTrue(len(raw_data) > 0)
        self.assertIsInstance(raw_data[0], dict)
        self.assertIn(constants.PROJECT_TYPE, raw_data[0])
        self.assertIn(constants.COUNTY, raw_data[0])
