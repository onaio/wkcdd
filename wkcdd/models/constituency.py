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

    def get_projects(self):
        """
        Get the list of projects associated with this county.
        """
        from wkcdd.models.helpers import (
            get_project_list, get_community_ids)
        return get_project_list(
            get_community_ids([self.id]))
