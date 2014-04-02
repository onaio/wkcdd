import datetime
from wkcdd.models import Location
from wkcdd.tests.test_base import TestBase
from wkcdd.models.project import(
    Project,
    ProjectType
)
from wkcdd.models.report import Report


class TestProject(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        project_type2 = ProjectType.get(ProjectType.id == 2)
        project1 = Project.get(Project.name == "Dairy Goat Project Center 2")

        self.assertEqual(project_type2.name, "Dairy Goat Project")
        self.assertEqual(project1.code, "JDCV")
        self.assertEqual(project1.community.name, "Bukusu")

    def test_project_can_retrieve_associated_reports(self):
        self.setup_test_data()
        project = Project.get(Project.code == "YH9T")
        self.assertEquals(len(project.reports), 1)

    def test_get_latest_report(self):
        self.setup_test_data()
        project = Project.get(Project.code == "WRTD")
        latest_report = Report.get(Report.submission_time ==
                                   datetime.datetime(2014, 3, 21))
        self.assertEqual(project.get_latest_report(), latest_report)
        self.assertEqual(
            [report.submission_time.day for report in project.reports],
            [21, 12, 10])

    def test_get_constituency(self):
        self.setup_test_data()
        project = Project.get(Project.code == "JDCV",
                              Project.name == "Dairy Goat Project Center 2")
        constituency = project.get_constituency(project.community)
        self.assertEquals(constituency.name, "Kakamega")

    def test_get_sub_county(self):
        self.setup_test_data()
        project = Project.get(Project.code == "JDCV",
                              Project.name == "Dairy Goat Project Center 2")
        constituency = project.get_constituency(project.community)
        sub_county = project.get_sub_county(constituency)
        self.assertEquals(sub_county.name, "Bungoma")

    def test_get_county(self):
        self.setup_test_data()
        project = Project.get(Project.code == "YH9T",
                              Project.name == "Dairy Goat Project Center 1")
        constituency = project.get_constituency(project.community)
        sub_county = project.get_sub_county(constituency)
        county = Project.get_county(sub_county)
        self.assertEquals(county.name, "Bungoma")
        self.assertEquals(county.parent_id, 0)

    def test_get_locations(self):
        self.setup_test_data()
        projects = Project.all()
        locations = Project.get_locations(projects)
        self.assertIsInstance(locations[1][0], Location)
        self.assertEquals(len(locations), 6)
