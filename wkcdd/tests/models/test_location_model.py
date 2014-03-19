from wkcdd.tests.test_base import TestBase

from wkcdd.models.location import(
    Location,
    LocationType
)


class TestLocation(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        location1 = Location.get(Location.id == 1)
        location_type1 = LocationType.get(LocationType.id == 1)

        self.assertEquals(location1.name, "Kakamega")
        self.assertEquals(location_type1.name, "constituency")

    def test_save_location_type(self):
        count = LocationType.count()
        location = LocationType(name='TestLocation')
        location.save()
        self.assertEquals(count+1, LocationType.count())
