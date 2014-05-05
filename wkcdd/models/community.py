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

    @classmethod
    def get_child_ids(cls, community_ids):
        return cls.get_child_class(), community_ids

    @classmethod
    def get_child_class(cls):
        from project import Project
        return Project
