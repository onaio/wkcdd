from wkcdd.models import Location

from wkcdd.tests.test_base import TestBase


class TestLocation(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        location1 = Location.get(Location.id == 1)

        self.assertEquals(location1.name, "Bungoma")
        self.assertEquals(location1.location_type, Location.COUNTY)
