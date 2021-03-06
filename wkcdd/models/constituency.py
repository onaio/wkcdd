from wkcdd.models.location import Location


class Constituency(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.CONSTITUENCY
    }

    @property
    def sub_county(self):
        return self.parent

    @sub_county.setter
    def sub_county(self, sub_county):
        self.parent = sub_county

    @classmethod
    def get_child_ids(cls, constituency_ids):
        from helpers import get_community_ids
        return cls.get_child_class(), get_community_ids(constituency_ids)

    @classmethod
    def get_child_class(cls):
        from community import Community
        return Community

    def get_projects(self, *criterion):
        """
        Get the list of projects associated with this Constituency.
        """
        from wkcdd.models.helpers import (
            get_project_list, get_community_ids)
        return get_project_list(
            get_community_ids([self.id]), *criterion)

    def get_project_ids(self, *criterion):
        """
        Get the project_ids associated with this Constituency.
        """
        from wkcdd.models.helpers import (
            get_project_ids, get_community_ids)
        return get_project_ids(
            get_community_ids([self.id]), *criterion)

    def is_found_in(self, location):
        return self.id == location.id or self.sub_county.is_found_in(location)

    @classmethod
    def get_rank(cls):
        return 3
