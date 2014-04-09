from wkcdd.models.location import Location


class SubCounty(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.SUB_COUNTY
    }

    @property
    def county(self):
        return self.parent

    @county.setter
    def county(self, county):
        self.parent = county