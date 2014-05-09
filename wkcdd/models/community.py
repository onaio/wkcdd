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
        from wkcdd.models import helpers
        return cls.get_child_class(), helpers.get_project_ids(community_ids)

    @classmethod
    def get_child_class(cls):
        from project import Project
        return Project

    def get_projects(self, *criterion):
        """
        Get the list of projects associated with this Community.
        """
        from wkcdd.models.helpers import get_project_list
        return get_project_list([self.id], *criterion)

    def is_found_in(self, location):
        return (self.id == location.id
                or self.constituency.is_found_in(location))

    @classmethod
    def get_rank(cls):
        return 4
