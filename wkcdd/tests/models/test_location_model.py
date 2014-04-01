from wkcdd.models.base import DBSession
from wkcdd.models import (
    Location, County, SubCounty, Constituency, Community, utils)

from wkcdd.tests.test_base import TestBase


class TestLocation(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        location1 = Location.get(Location.id == 1)

        self.assertEquals(location1.name, "Bungoma")
        self.assertEquals(location1.location_type, Location.COUNTY)

    def test_sub_county_ids_from_county_ids(self):
        self.setup_test_data()
        # get the county's id
        county_id = County.get(County.name == "Bungoma").id
        # get the sub-county ids
        sub_county_ids = utils.get_sub_county_ids([county_id])
        self.assertEqual(len(sub_county_ids), 1)
        sub_county = SubCounty.get(SubCounty.id == sub_county_ids[0])
        self.assertEqual(sub_county.name, "Bungoma")

    def test_constituency_ids_from_sub_county_ids(self):
        self.setup_test_data()
        # get the sub county ids
        sub_county_ids = [sub_county.id for sub_county in SubCounty.all()]
        # get the constituency ids
        constituency_ids = utils.get_constituency_ids(sub_county_ids)
        self.assertEqual(len(constituency_ids), 1)
        # get the constituency(s)
        constituency = Constituency.get(Constituency.id == constituency_ids[0])
        self.assertEqual(constituency.name, "Kakamega")

    def test_community_ids_from_constituency_ids(self):
        self.setup_test_data()
        # get the constituency ids
        constituency_ids = [c.id for c in Constituency.all()]
        community_ids = utils.get_community_ids(constituency_ids)
        self.assertEqual(len(community_ids), 2)
        community_names = DBSession.query(
            Community.name).filter(Community.id.in_(community_ids)).all()
        self.assertListEqual(
            [c.name for c in community_names], ['Maragoli', 'Bukusu'])