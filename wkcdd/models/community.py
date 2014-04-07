from wkcdd.models.location import Location


class Community(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.COMMUNITY
    }
