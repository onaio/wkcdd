from wkcdd.models import Location
from wkcdd.tests.test_base import TestBase

from wkcdd.models.project import(
    Project,
    ProjectType
)


class TestProject(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        project_type1 = ProjectType.get(ProjectType.id == 1)
        project1 = Project.get(Project.name == "Dairy Cow Project Center 1")

        self.assertEquals(project_type1.name, "Dairy Cow Project")
        self.assertEquals(project1.code, "FR3A")
        self.assertEquals(project1.community.name, "Maragoli")
        self.assertEquals(project1.community.constituency.name, "Kakamega")

    def test_project_can_retrieve_associated_reports(self):
        self.setup_test_data()
        project = Project.get(Project.code == "YH9T")
        self.assertEquals(len(project.reports), 1)

    def test_get_sub_county(self):
        self.setup_test_data()
        project = Project.get(Project.code == "JDCV",
                              Project.name == "Dairy Goat Project Center 2")
        sub_county = project.get_sub_county()
        self.assertEquals(sub_county.name, "Bungoma")

    def test_get_county(self):
        self.setup_test_data()
        project = Project.get(Project.code == "YH9T",
                              Project.name == "Dairy Goat Project Center 1")
        sub_county = project.get_sub_county()
        county = Project.get_county(sub_county)
        self.assertEquals(county.name, "Bungoma")
        self.assertEquals(county.parent_id, 0)

    def test_get_locations(self):
        self.setup_test_data()
        projects = Project.all()
        locations = Project.get_locations(projects)
        self.assertIsInstance(locations[1][0], Location)
        self.assertEquals(len(locations), 3)
