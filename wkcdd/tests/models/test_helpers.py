from wkcdd.models.base import DBSession
from wkcdd.models import (
    County, SubCounty, Constituency, Community, helpers, Project)

from wkcdd import constants
from wkcdd.tests.test_base import TestBase


class TestHelpers(TestBase):

    def test_sub_county_ids_from_county_ids(self):
        self.setup_test_data()
        # get the county's id
        county_id = County.get(County.name == "Bungoma").id
        # get the sub-county ids
        sub_county_ids = helpers.get_sub_county_ids([county_id])
        self.assertEqual(len(sub_county_ids), 1)
        sub_county = SubCounty.get(SubCounty.id == sub_county_ids[0])
        self.assertEqual(sub_county.name, "Bungoma")

    def test_constituency_ids_from_sub_county_ids(self):
        self.setup_test_data()
        # get the sub county ids
        sub_county_ids = [sub_county.id for sub_county in SubCounty.all()]
        # get the constituency ids
        constituency_ids = helpers.get_constituency_ids(sub_county_ids)
        self.assertEqual(len(constituency_ids), 2)
        # get the constituency(s)
        constituency = Constituency.get(Constituency.id == constituency_ids[0])
        self.assertEqual(constituency.name, "Kakamega")

    def test_community_ids_from_constituency_ids(self):
        self.setup_test_data()
        # get the constituency ids
        constituency_ids = [c.id for c in Constituency.all()]
        community_ids = helpers.get_community_ids(constituency_ids)
        self.assertEqual(len(community_ids), 3)
        community_names = DBSession.query(
            Community.name).filter(Community.id.in_(community_ids)).all()
        self.assertListEqual(
            [c.name for c in community_names],
            ['Rwatama', 'Maragoli', 'Bukusu'])

    def test_get_project_list_from_community_ids(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Maragoli")
        community_ids = [community.id]
        projects = helpers.get_project_list(community_ids)
        self.assertEqual(len(projects), len(community.projects))
        self.assertEqual(projects[0].name, "Dairy Goat Project Center 1")

    def test_get_project_list_by_type_from_community_ids(self):
        self.setup_community_test_data()
        community_ids = [Community.get(Community.name == "lutacho").id]
        # test retrieval of dairy cow projects
        projects = helpers.get_project_list(
            community_ids,
            Project.sector == constants.DAIRY_COWS_PROJECT_REGISTRATION)
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0].name, "Cow project 1")

        # test retrieval of dairy goat projects
        projects = helpers.get_project_list(
            community_ids,
            Project.sector == constants.DAIRY_GOAT_PROJECT_REGISTRATION)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, "Goat project 1")

        # test retrieval of Motocycle projects
        projects = helpers.get_project_list(
            community_ids,
            Project.sector == constants.BODABODA_PROJECT_REGISTRATION)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, "Bodaboda project 1")

    def test_get_project_types(self):
        self.setup_community_test_data()
        community_ids = [c.id for c in Community.all()]
        project_types = sorted(helpers.get_project_types(
            community_ids),
            key=lambda x: x[0])
        # Diary Cow, Dairy Goat and Boda Boda
        expected_list = sorted([(reg, report, label)
                               for (reg,
                                    report,
                                    label) in constants.PROJECT_TYPE_MAPPING
                               if reg in
                               [constants.DAIRY_GOAT_PROJECT_REGISTRATION,
                                constants.DAIRY_COWS_PROJECT_REGISTRATION,
                                constants.BODABODA_PROJECT_REGISTRATION]],
                               key=lambda x: x[0])
        self.assertListEqual(expected_list, project_types)

    def test_get_children_by_level_for_counties_by_community(self):
        self.setup_test_data()
        county = County.get(County.name == "Bungoma")
        child_ids = helpers.get_children_by_level(
            [county.id], County, Community)
        child_names = [c.name for c in Community.all(
            Community.id.in_(child_ids))]
        self.assertEqual(
            sorted([u'Maragoli', u'Bukusu']), sorted(child_names))

    def test_get_project_ids(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Maragoli")
        projects = Project.all(Project.code.in_(["7CWA", "FR3A"]))

        project_ids = helpers.get_project_ids([community.id])
        self.assertEqual(project_ids, [p.id for p in projects])
