from wkcdd.models.location import Location


class Constituency(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.CONSTITUENCY
    }
