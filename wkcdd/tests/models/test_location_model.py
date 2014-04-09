from wkcdd.models import *
from wkcdd.tests.test_base import TestBase


class TestLocation(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        location1 = Location.get(Location.id == 1)

        self.assertEquals(location1.name, "Bungoma")
        self.assertEquals(location1.location_type, Location.COUNTY)

    def test_community_get_constituency(self):
        self.setup_test_data()
        community = Community.get(Community.name == "Rwatama")
        self.assertEqual(community.constituency.name, "Amagoro")

    def test_constituency_get_sub_county(self):
        self.setup_test_data()
        constituency = Constituency.get(Constituency.name == "Kakamega")
        self.assertEqual(constituency.sub_county.name, "Bungoma")

    def test_sub_county_get_county(self):
        self.setup_test_data()
        sub_county = SubCounty.get(SubCounty.name == "Bungoma")
        self.assertEqual(sub_county.county.name, "Bungoma")