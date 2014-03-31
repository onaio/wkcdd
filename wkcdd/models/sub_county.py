from wkcdd.models.location import Location


class SubCounty(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.SUB_COUNTY
    }
