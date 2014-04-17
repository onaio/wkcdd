import datetime
from wkcdd.models import Location
from wkcdd.tests.test_base import TestBase
from wkcdd.models.project import Project
from wkcdd.models.report import Report
from wkcdd import constants


class TestProject(TestBase):
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
                              Project.name == "Dairy Cow Project Center 1")
        constituency = project.get_constituency(project.community)
        sub_county = project.get_sub_county(constituency)
        county = Project.get_county(sub_county)
        self.assertEquals(county.name, "Bungoma")
        self.assertIsNone(county.parent_id)

    def test_get_locations(self):
        self.setup_test_data()
        projects = Project.all()
        locations = Project.get_locations(projects)
        self.assertIsInstance(locations[1][0], Location)
        self.assertEquals(len(locations), 7)

    def test_get_latlong(self):
        self.setup_test_data()
        project1 = Project.get(Project.code == 'JDCV')
        self.assertEquals(project1.latlong, ["0.0", "0.0"])
        project2 = Project.get(Project.code == 'WRTD')
        self.assertEquals(project2.latlong, ["0.1231", "34.1213"])
        project3 = Project.get(Project.code == 'YH9T')
        self.assertFalse(project3.latlong)

    def test_sector_name(self):
        self.setup_test_data()
        project1 = Project.get(Project.code == 'JDCV')
        sector_name = project1.sector_name
        self.assertEqual(sector_name, "Dairy Goat")
