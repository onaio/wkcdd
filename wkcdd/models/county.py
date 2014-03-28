from wkcdd.models.location import Location


class County(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.COUNTY
    }
