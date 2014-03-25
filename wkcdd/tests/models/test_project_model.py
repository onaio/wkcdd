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
