import datetime

from wkcdd.tests.test_base import TestBase

from wkcdd.models.project import(
    Project,
    ProjectType
)

from wkcdd.models.report import Report


class TestProject(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        project_type1 = ProjectType.get(ProjectType.id == 1)
        project1 = Project.get(Project.name == "Dairy Cow Project Center 1")

        self.assertEqual(project_type1.name, "Dairy Cow Project")
        self.assertEqual(project1.code, "FR3A")
        self.assertEqual(project1.community.name, "Maragoli")
        self.assertEqual(project1.community.constituency.name, "Kakamega")

    def test_project_can_retrieve_associated_reports(self):
        self.setup_test_data()
        project = Project.get(Project.code == "YH9T")
        self.assertEqual(len(project.reports), 1)

    def test_get_latest_report(self):
        self.setup_test_data()
        project = Project.get(Project.code == "WRTD")
        latest_report = Report.get(Report.submission_time ==
                                   datetime.datetime(2014, 3, 21))
        self.assertEqual(project.get_latest_report(), latest_report)
        self.assertEqual(
            [report.submission_time.day for report in project.reports],
            [21, 12, 10])
