from wkcdd.models.location import Location


class Community(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.COMMUNITY
    }

    @property
    def constituency(self):
        return self.parent

    @constituency.setter
    def constituency(self, constituency):
        self.parent = constituency